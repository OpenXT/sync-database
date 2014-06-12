#
# Copyright (c) 2012 Citrix Systems, Inc.
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

import ConfigParser
import tempfile

import sync_db.configuration

def test_generate_config(db):
    input_text = ("SERVER\n"
                  "SYS_PASSWORD\n"
                  "PREFIX\n"
                  "OWNER_PASSWORD\n"
                  "ADMIN_PASSWORD\n"
                  "LICENSE_PASSWORD\n"
                  "SERVER_PASSWORD\n")

    with tempfile.NamedTemporaryFile() as f:
        db.run(["generate-config", f.name], input_text=input_text)

        parser = ConfigParser.RawConfigParser()
        parser.readfp(f)

    expected = {"oracle_server":         "SERVER",
                "sys_password":          "SYS_PASSWORD",
                "sync_owner_user":       "PREFIX_owner",
                "sync_owner_password":   "OWNER_PASSWORD",
                "sync_admin_user":       "PREFIX_admin",
                "sync_admin_password":   "ADMIN_PASSWORD",
                "sync_license_user":     "PREFIX_license",
                "sync_license_password": "LICENSE_PASSWORD",
                "sync_server_user":      "PREFIX_server",
                "sync_server_password":  "SERVER_PASSWORD"}

    config_section = sync_db.configuration.CONFIG_SECTION

    assert parser.sections() == [config_section]
    assert parser.defaults() == {}
    assert (dict(parser.items(config_section)) == expected)

def test_get_schema_dir(db):
    db.run(["get-schema-dir"])
