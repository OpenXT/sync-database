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

import cx_Oracle

import sync_db.error

class SyncServer:
    def __init__(self, connection):
        self.connection = connection

    def get_device_secret(self, device_uuid):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            shared_secret = cursor.callfunc("sync_server.get_device_secret",
                                            cx_Oracle.STRING,
                                            keywordParameters={
                                                "device_uuid": device_uuid})
        return shared_secret

    def get_device_state(self, device_uuid):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            device_info = self.connection.cursor()
            device_config = self.connection.cursor()
            vm_instances = self.connection.cursor()
            vm_instance_config = self.connection.cursor()
            vm_instance_disks = self.connection.cursor()
            disks = self.connection.cursor()

            cursor.callproc("sync_server.get_device_state",
                            keywordParameters={
                                "device_uuid": device_uuid,
                                "device_info": device_info,
                                "device_config": device_config,
                                "vm_instances": vm_instances,
                                "vm_instance_config": vm_instance_config,
                                "vm_instance_disks": vm_instance_disks,
                                "disks": disks})

        return (self._fetch_only_row(device_info),
                device_config.fetchall(),
                vm_instances.fetchall(),
                vm_instance_config.fetchall(),
                vm_instance_disks.fetchall(),
                disks.fetchall())

    def get_disk_path(self, device_uuid, disk_uuid):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            file_path = cursor.callfunc("sync_server.get_disk_path",
                                        cx_Oracle.STRING,
                                        keywordParameters={
                                            "device_uuid": device_uuid,
                                            "disk_uuid": disk_uuid})
        return file_path

    def get_repo_path(self, device_uuid, repo_uuid):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            file_path = cursor.callfunc(
                "sync_server.get_repo_path",
                cx_Oracle.STRING,
                keywordParameters={
                    "device_uuid": device_uuid,
                    "repo_uuid": repo_uuid})
        return file_path

    def report_device_state(self, device_uuid, release, build):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            file_path = cursor.callproc(
                "sync_server.report_device_state",
                keywordParameters={
                    "device_uuid": device_uuid,
                    "release": release,
                    "build": build})

    def _fetch_only_row(self, cursor):
        rows = cursor.fetchall()
        assert len(rows) == 1
        return rows[0]
