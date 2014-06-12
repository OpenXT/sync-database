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

import sync_db.error

class SyncAdmin:
    def __init__(self, connection):
        self.connection = connection

    def add_device(self, device_name, repo_uuid=None, config=None):
        if config is None:
            config = []

        with sync_db.error.convert():
            cursor = self.connection.cursor()
            device_uuid = cursor.callfunc(
                "sync_admin.add_device",
                cx_Oracle.STRING,
                keywordParameters={
                    "device_name": device_name,
                    "repo_uuid": repo_uuid,
                    "config": config})
            return device_uuid

    def add_disk(self, disk_name, disk_type, file_path, file_size, file_hash,
                 encryption_key, shared, read_only):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            disk_uuid = cursor.callfunc("sync_admin.add_disk",
                                        cx_Oracle.STRING,
                                        keywordParameters={
                                            "disk_name": disk_name,
                                            "disk_type": disk_type,
                                            "file_path": file_path,
                                            "file_size": file_size,
                                            "file_hash": file_hash,
                                            "encryption_key": encryption_key,
                                            "shared": shared,
                                            "read_only": read_only})
            return disk_uuid

    def add_repo(self, release, build, file_path, file_size, file_hash):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            repo_uuid = cursor.callfunc("sync_admin.add_repo",
                                        cx_Oracle.STRING,
                                        keywordParameters={
                                            "release": release,
                                            "build": build,
                                            "file_path": file_path,
                                            "file_size": file_size,
                                            "file_hash": file_hash})
            return repo_uuid

    def add_vm(self, vm_name, disk_uuids, config=None):
        if config is None:
            config = []

        with sync_db.error.convert():
            cursor = self.connection.cursor()
            vm_uuid = cursor.callfunc("sync_admin.add_vm",
                                      cx_Oracle.STRING,
                                      keywordParameters={
                                          "vm_name": vm_name,
                                          "disk_uuids": disk_uuids,
                                          "config": config})
            return vm_uuid

    def add_vm_instance(self, device_uuid, vm_uuid, vm_instance_name):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            vm_instance_uuid = cursor.callfunc("sync_admin.add_vm_instance",
                                   cx_Oracle.STRING,
                                   keywordParameters={
                                       "device_uuid": device_uuid,
                                       "vm_uuid": vm_uuid,
                                       "vm_instance_name": vm_instance_name})
            return vm_instance_uuid

    def complete_device_uuid(self, partial_device_uuid):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            device_uuids = cursor.callfunc("sync_admin.complete_device_uuid",
                               cx_Oracle.CURSOR,
                               keywordParameters={
                                   "partial_device_uuid": partial_device_uuid})
            return self._fetch_only_column(device_uuids)

    def complete_disk_uuid(self, partial_disk_uuid):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            disk_uuids = cursor.callfunc(
                "sync_admin.complete_disk_uuid",
                cx_Oracle.CURSOR,
                keywordParameters={
                    "partial_disk_uuid": partial_disk_uuid})
            return self._fetch_only_column(disk_uuids)

    def complete_repo_uuid(self, partial_repo_uuid):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            repo_uuids = cursor.callfunc(
                "sync_admin.complete_repo_uuid",
                cx_Oracle.CURSOR,
                keywordParameters={
                    "partial_repo_uuid": partial_repo_uuid})
            return self._fetch_only_column(repo_uuids)

    def complete_vm_uuid(self, partial_vm_uuid):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            vm_uuids = cursor.callfunc(
                "sync_admin.complete_vm_uuid",
                cx_Oracle.CURSOR,
                keywordParameters={
                    "partial_vm_uuid": partial_vm_uuid})
            return self._fetch_only_column(vm_uuids)

    def complete_vm_instance_uuid(self, partial_vm_instance_uuid,
                                  include_unremoved=True,
                                  include_removed=False):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            vm_instance_uuids = cursor.callfunc(
                "sync_admin.complete_vm_instance_uuid",
                cx_Oracle.CURSOR,
                keywordParameters={
                    "partial_vm_instance_uuid": partial_vm_instance_uuid,
                    "include_unremoved": include_unremoved,
                    "include_removed": include_removed})
            return self._fetch_only_column(vm_instance_uuids)

    def get_device(self, device_uuid):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            device = cursor.callfunc("sync_admin.get_device",
                                     cx_Oracle.CURSOR,
                                     keywordParameters={
                                         "device_uuid": device_uuid})
            return self._fetch_only_row(device)

    def get_device_config(self, device_uuid):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            config = cursor.callfunc("sync_admin.get_device_config",
                                     cx_Oracle.CURSOR,
                                     keywordParameters={
                                         "device_uuid": device_uuid})
            return config.fetchall()

    def get_device_secret(self, device_uuid):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            shared_secret = cursor.callfunc("sync_admin.get_device_secret",
                                            cx_Oracle.STRING,
                                            keywordParameters={
                                                "device_uuid": device_uuid})
            return shared_secret

    def get_disk(self, disk_uuid):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            disk = cursor.callfunc("sync_admin.get_disk",
                                   cx_Oracle.CURSOR,
                                   keywordParameters={
                                       "disk_uuid": disk_uuid})
            return self._fetch_only_row(disk)

    def get_disk_key(self, disk_uuid):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            encryption_key = cursor.callfunc("sync_admin.get_disk_key",
                                             cx_Oracle.STRING,
                                             keywordParameters={
                                                 "disk_uuid": disk_uuid})
            return encryption_key

    def get_licensing(self):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            licensing = cursor.callfunc(
                "sync_admin.get_licensing",
                cx_Oracle.CURSOR)
            return self._fetch_only_row(licensing)

    def get_repo(self, repo_uuid):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            repo = cursor.callfunc(
                "sync_admin.get_repo",
                cx_Oracle.CURSOR,
                keywordParameters={
                    "repo_uuid": repo_uuid})
            return self._fetch_only_row(repo)

    def get_report(self, device_uuid):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            device_report = cursor.callfunc(
                "sync_admin.get_report",
                cx_Oracle.CURSOR,
                keywordParameters={
                    "device_uuid": device_uuid})
            return self._fetch_only_row(device_report)

    def get_vm(self, vm_uuid):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            vm = cursor.callfunc("sync_admin.get_vm",
                                 cx_Oracle.CURSOR,
                                 keywordParameters={
                                     "vm_uuid": vm_uuid})
            return self._fetch_only_row(vm)

    def get_vm_config(self, vm_uuid):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            config = cursor.callfunc("sync_admin.get_vm_config",
                                     cx_Oracle.CURSOR,
                                     keywordParameters={
                                         "vm_uuid": vm_uuid})
            return config.fetchall()

    def get_vm_instance(self, vm_instance_uuid):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            vm_instance = cursor.callfunc(
                "sync_admin.get_vm_instance",
                cx_Oracle.CURSOR,
                keywordParameters={
                    "vm_instance_uuid": vm_instance_uuid})
            return self._fetch_only_row(vm_instance)

    def list_all_files(self):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            disks = self.connection.cursor()
            repos = self.connection.cursor()
            cursor.callproc("sync_admin.list_all_files",
                             keywordParameters={
                                 "disks": disks,
                                 "repos": repos})
            return disks.fetchall(), repos.fetchall()

    def list_devices(self, device_name=None, repo_uuid=None, no_repo=False,
                     vm_uuid=None):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            devices = cursor.callfunc("sync_admin.list_devices",
                                      cx_Oracle.CURSOR,
                                      keywordParameters={
                                          "device_name": device_name,
                                          "repo_uuid": repo_uuid,
                                          "no_repo": no_repo,
                                          "vm_uuid": vm_uuid})
            return devices.fetchall()

    def list_disks(self, disk_name=None, disk_type=None, file_path=None,
                   file_hash=None, vm_uuid=None, vm_instance_uuid=None,
                   unused=False):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            disks = cursor.callfunc("sync_admin.list_disks",
                                    cx_Oracle.CURSOR,
                                    keywordParameters={
                                        "disk_name": disk_name,
                                        "disk_type": disk_type,
                                        "file_path": file_path,
                                        "file_hash": file_hash,
                                        "vm_uuid": vm_uuid,
                                        "vm_instance_uuid": vm_instance_uuid,
                                        "unused": unused})
            return disks.fetchall()

    def list_repos(self, release=None, build=None, file_path=None,
                   file_hash=None, unused=False):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            repos = cursor.callfunc(
                "sync_admin.list_repos",
                cx_Oracle.CURSOR,
                keywordParameters={
                    "release": release,
                    "build": build,
                    "file_path": file_path,
                    "file_hash": file_hash,
                    "unused": unused})
            return repos.fetchall()

    def list_vms(self, vm_name=None, device_uuid=None, disk_uuid=None,
                 unused=False):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            vms = cursor.callfunc("sync_admin.list_vms",
                                  cx_Oracle.CURSOR,
                                  keywordParameters={
                                      "vm_name": vm_name,
                                      "device_uuid": device_uuid,
                                      "disk_uuid": disk_uuid,
                                      "unused": unused})
            return vms.fetchall()

    def list_vm_instances(self, vm_instance_name=None, device_uuid=None,
                          vm_uuid=None, disk_uuid=None, removed=False):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            vm_instances = cursor.callfunc(
                "sync_admin.list_vm_instances",
                cx_Oracle.CURSOR,
                keywordParameters={
                    "vm_instance_name": vm_instance_name,
                    "device_uuid": device_uuid,
                    "vm_uuid": vm_uuid,
                    "disk_uuid": disk_uuid,
                    "removed": removed})
            return vm_instances.fetchall()

    def lock_vm_instance(self, vm_instance_uuid):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            cursor.callproc("sync_admin.lock_vm_instance",
                            keywordParameters={
                                "vm_instance_uuid": vm_instance_uuid})

    def modify_device_config(self, device_uuid, config, replace=False):
        if config is None:
            config = []

        with sync_db.error.convert():
            cursor = self.connection.cursor()
            cursor.callproc("sync_admin.modify_device_config",
                            keywordParameters={
                                "device_uuid": device_uuid,
                                "config": config,
                                "replace": replace})

    def modify_device_repo(self, device_uuid, repo_uuid):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            cursor.callproc("sync_admin.modify_device_repo",
                            keywordParameters={
                                "device_uuid": device_uuid,
                                "repo_uuid": repo_uuid})

    def modify_vm_config(self, vm_uuid, config, replace=False):
        if config is None:
            config = []

        with sync_db.error.convert():
            cursor = self.connection.cursor()
            cursor.callproc("sync_admin.modify_vm_config",
                            keywordParameters={
                                "vm_uuid": vm_uuid,
                                "config": config,
                                "replace": replace})

    def modify_vm_instance_name(self, vm_instance_uuid, vm_instance_name):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            cursor.callproc("sync_admin.modify_vm_instance_name",
                            keywordParameters={
                                "vm_instance_uuid": vm_instance_uuid,
                                "vm_instance_name": vm_instance_name})

    def purge_vm_instance(self, vm_instance_uuid):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            cursor.callproc("sync_admin.purge_vm_instance",
                            keywordParameters={
                                "vm_instance_uuid": vm_instance_uuid})

    def readd_vm_instance(self, vm_instance_uuid):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            cursor.callproc("sync_admin.readd_vm_instance",
                            keywordParameters={
                                "vm_instance_uuid": vm_instance_uuid})

    def remove_device(self, device_uuid, cascade=False):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            cursor.callproc("sync_admin.remove_device",
                            keywordParameters={
                                "device_uuid": device_uuid,
                                "cascade": cascade})

    def remove_disk(self, disk_uuid):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            cursor.callproc("sync_admin.remove_disk",
                            keywordParameters={
                                "disk_uuid": disk_uuid})

    def remove_repo(self, repo_uuid):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            cursor.callproc("sync_admin.remove_repo",
                            keywordParameters={
                                "repo_uuid": repo_uuid})

    def remove_vm(self, vm_uuid, cascade=False):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            cursor.callproc("sync_admin.remove_vm",
                            keywordParameters={
                                "vm_uuid": vm_uuid,
                                "cascade": cascade})

    def remove_vm_instance(self, vm_instance_uuid, hard_removal):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            cursor.callproc("sync_admin.remove_vm_instance",
                            keywordParameters={
                                "vm_instance_uuid": vm_instance_uuid,
                                "hard_removal": hard_removal})

    def reset_device_secret(self, device_uuid):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            cursor.callproc("sync_admin.reset_device_secret",
                            keywordParameters={
                                "device_uuid": device_uuid})

    def unlock_vm_instance(self, vm_instance_uuid):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            cursor.callproc("sync_admin.unlock_vm_instance",
                            keywordParameters={
                                "vm_instance_uuid": vm_instance_uuid})

    def verify_database(self):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            cursor.callproc("sync_admin.verify_database",
                            keywordParameters={})

    def _fetch_only_row(self, cursor):
        rows = cursor.fetchall()
        assert len(rows) == 1
        return rows[0]

    def _fetch_only_column(self, cursor):
        assert len(cursor.description) == 1
        return [row[0] for row in cursor]
