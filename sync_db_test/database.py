#
# Copyright (c) 2013 Citrix Systems, Inc.
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import cx_Oracle
import json
import os
import subprocess
import tempfile

import sync_db.configuration

import connect
import sync_admin
import sync_license
import sync_server

class Database:
    _UNKNOWN, _MISSING, _INSTALLED = range(3)

    ALL_TABLES = ["device",
                  "device_config",
                  "device_license",
                  "disk",
                  "repo",
                  "report_device",
                  "synchronizer",
                  "version",
                  "vm",
                  "vm_config",
                  "vm_disk",
                  "vm_instance"]

    def __init__(self, config_file=None):
        self._state = self._UNKNOWN
        self._config = sync_db.configuration.read_config(config_file)

        self._admin = None
        self._license = None
        self._server = None
        self._owner = None

        schema_dir = self.run(["get-schema-dir"],
                              collect_output=True).rstrip()

        with open(os.path.join(schema_dir, "schema.json"), "r") as f:
            self._metadata = json.load(f)

        # By default, the Oracle client library adds SA_NOCLDWAIT to the
        # SIGCHLD handler, which interferes with the python subprocess module,
        # causing it to fail with ECHILD errors.
        #
        # Turn off this behaviour by setting the "bequeath_detach" parameter
        # in a temporary sqlnet.ora file. Certain web pages suggest that it can
        # be set as an environment variable BEQUEATH_DETACH, but this doesn't
        # appear to work.
        self._temp_dir = tempfile.mkdtemp()
        self._sqlnet_ora_file = os.path.join(self._temp_dir, "sqlnet.ora")
        os.environ["TNS_ADMIN"] = self._temp_dir
        with open(self._sqlnet_ora_file, "w") as f:
            f.write("bequeath_detach = yes\n")

    def tear_down(self):
        os.remove(self._sqlnet_ora_file)
        os.rmdir(self._temp_dir)
        del os.environ["TNS_ADMIN"]

    def ensure_missing(self):
        if self._state != self._MISSING:
            self.run(["destroy", "--force"])
            self._state = self._MISSING

    def ensure_clean(self):
        if self._state == self._UNKNOWN:
            self.run(["destroy", "--force"])
            self._state = self._MISSING

        if self._state == self._MISSING:
            self.run(["install"])
            self._state = self._INSTALLED

        self._clean()

    def run(self, command, input_text=None, collect_output=False):
        self._state = self._UNKNOWN
        self._admin = None
        self._license = None
        self._server = None
        self._owner = None
        args = ["./sync-database"] + command

        input_file = None
        output_file = None

        try:
            if input_text is not None:
                input_file = tempfile.TemporaryFile()
                input_file.write(input_text)
                input_file.seek(0)

            if collect_output:
                output_file = tempfile.TemporaryFile()

            subprocess.check_call(args, stdin=input_file, stdout=output_file)

            if output_file:
                output_file.seek(0)
                return output_file.read()
        finally:
            if input_file:
                input_file.close()

            if output_file:
                output_file.close()

    def _clean(self):
        for connection in [self._admin,
                           self._license,
                           self._server,
                           self._owner]:
            if connection is not None:
                connection.connection.rollback()

        owner = self.get_owner_connection()
        owner.connection.cursor().execute("set constraints all deferred")

        for table in self.ALL_TABLES:
            owner.connection.cursor().execute("delete from " + table)

        owner.connection.cursor().execute(
            "insert into synchronizer "
            "( "
            "    num_offline_licenses "
            ") "
            "values "
            "( "
            "    null "
            ")")

        owner.connection.cursor().execute(
            "insert into version "
            "( "
            "    current_version, "
            "    installing_version "
            ") "
            "values "
            "( "
            "    :current_version, "
            "    null "
            ")",
            current_version=self.get_target_version())

        owner.connection.commit()

    def get_admin_connection(self):
        if self._admin is None:
            self._admin = connect.AdminConnection(
                self._config["sync_admin_user"],
                self._config["sync_admin_password"],
                self._config["oracle_server"])
        return self._admin

    def get_license_connection(self):
        if self._license is None:
            self._license = connect.LicenseConnection(
                self._config["sync_license_user"],
                self._config["sync_license_password"],
                self._config["oracle_server"])
        return self._license

    def get_owner_connection(self):
        if self._owner is None:
            self._owner = connect.OwnerConnection(
                self._config["sync_owner_user"],
                self._config["sync_owner_password"],
                self._config["oracle_server"])
        return self._owner

    def get_server_connection(self):
        if self._server is None:
            self._server = connect.ServerConnection(
                self._config["sync_server_user"],
                self._config["sync_server_password"],
                self._config["oracle_server"])
        return self._server

    def get_target_version(self):
        return self._metadata["version"]

    def get_upgrade_from(self):
        return self._metadata["upgrade-from"]

    def run_version(self):
        output = self.run(["version"], collect_output=True)
        data = {}

        for line in output.splitlines():
            fields = line.split(": ", 1)
            if len(fields) == 2:
                data[fields[0]] = fields[1]

        return data["Target schema version"], data["Database schema version"]
