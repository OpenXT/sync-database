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
import os
import py.test
import schema
import subprocess

import sync_db.error

import raises

def test_upgrade(missing_db):
    db = missing_db

    db.run(["install"])
    target_schema = schema.dump_schema(db)

    target_version = db.get_target_version()
    old_versions = db.get_upgrade_from()

    assert (sorted(os.listdir("sync_db_test/old-schema")) ==
            sorted(old_versions))

    for old_version in old_versions:
        db.run(["destroy", "--force"])

        db.run(["--schema-dir",
                "sync_db_test/old-schema/" + old_version,
                "install"])
        assert db.run_version() == (target_version, old_version)

        db.run(["upgrade"])
        assert db.run_version() == (target_version, target_version)

        upgraded_schema = schema.dump_schema(db)
        schema.compare_schemas(target_schema,
                               upgraded_schema,
                               "installed version {0}".format(target_version),
                               "upgraded from version {0} to version "
                                   "{1}".format(old_version, target_version))

def test_upgrade_forced(missing_db):
    db = missing_db

    target_version = db.get_target_version()

    db.run(["install"])
    target_schema = schema.dump_schema(db)

    with py.test.raises(subprocess.CalledProcessError):
        db.run(["upgrade"])

    db.run(["upgrade", "--force"])
    assert db.run_version() == (target_version, target_version)

    upgraded_schema = schema.dump_schema(db)
    schema.compare_schemas(target_schema,
                           upgraded_schema,
                           "installed version {0}".format(target_version),
                           "upgraded (forced) from version {0} to version "
                               "{1}".format(target_version, target_version))

def test_upgrade_unsupported(missing_db):
    db = missing_db

    db.run(["install"])

    owner = db.get_owner_connection()
    admin = db.get_admin_connection()

    cursor = owner.connection.cursor()
    cursor.execute("update version "
                   "set current_version = 'bad'")
    owner.connection.commit()

    with py.test.raises(subprocess.CalledProcessError):
        db.run(["upgrade", "--force"])

    cursor = owner.connection.cursor()
    cursor.execute("update version "
                   "set installing_version = 'dummy'")
    owner.connection.commit()

    with raises.sync_error(sync_db.error.UPGRADE_INCOMPLETE):
        admin.sa.add_vm("name", [])

    cursor = owner.connection.cursor()
    cursor.execute("update version "
                   "set current_version = null")
    owner.connection.commit()

    with raises.sync_error(sync_db.error.INSTALLATION_INCOMPLETE):
        admin.sa.add_vm("name", [])

def test_upgrade_retry(missing_db):
    db = missing_db

    db.run(["install"])
    target_schema = schema.dump_schema(db)

    db.run(["upgrade", "--to", "2", "--force"])

    target_version = db.get_target_version()
    assert db.run_version() == (target_version,
                                "incomplete upgrade from version {0} to "
                                "{1}".format(target_version, target_version))

    with py.test.raises(subprocess.CalledProcessError):
        db.run(["install"])
    with py.test.raises(subprocess.CalledProcessError):
        db.run(["upgrade", "--force"])

    db.run(["upgrade", "--force", "--retry"])
    assert db.run_version() == (target_version, target_version)

    upgraded_schema = schema.dump_schema(db)
    schema.compare_schemas(target_schema,
                           upgraded_schema,
                           "installed version {0}".format(target_version),
                           "upgraded (forced with retry) from version {0} to "
                                "version {1}".format(target_version,
                                                     target_version))

def test_upgrade_check(missing_db):
    def add_user(connection, user_name, auth_token):
        with sync_db.error.convert():
            cursor = connection.cursor()
            user_uuid = cursor.callfunc("sync_admin.add_user",
                                        cx_Oracle.STRING,
                                        keywordParameters={
                                            "user_name": user_name,
                                            "auth_token": auth_token})
            return user_uuid

    def add_user_to_device(connection, user_uuid, device_uuid):
        with sync_db.error.convert():
            cursor = connection.cursor()
            cursor.callproc("sync_admin.add_user_to_device",
                            keywordParameters={
                                "user_uuid": user_uuid,
                                "device_uuid": device_uuid})

    def add_vm_instance(connection, device_uuid, user_uuid, vm_uuid,
                        vm_instance_name):
        with sync_db.error.convert():
            cursor = connection.cursor()
            vm_instance_uuid = cursor.callfunc("sync_admin.add_vm_instance",
                                   cx_Oracle.STRING,
                                   keywordParameters={
                                       "device_uuid": device_uuid,
                                       "user_uuid": user_uuid,
                                       "vm_uuid": vm_uuid,
                                       "vm_instance_name": vm_instance_name})
            return vm_instance_uuid

    db = missing_db

    target_version = db.get_target_version()
    old_version = "2"

    db.run(["--schema-dir",
            "sync_db_test/old-schema/" + old_version,
            "install"])
    assert db.run_version() == (target_version, old_version)

    admin = db.get_admin_connection()

    vm = admin.sa.add_vm("name", [])
    device = admin.sa.add_device("name")

    user1 = add_user(admin.sa.connection, "name1", "token1")
    user2 = add_user(admin.sa.connection, "name2", "token1")

    add_user_to_device(admin.sa.connection, user1, device)
    add_user_to_device(admin.sa.connection, user2, device)

    vm_instance1 = add_vm_instance(admin.sa.connection, device, user1, vm, "name1")
    vm_instance2 = add_vm_instance(admin.sa.connection, device, user2, vm, "name2")

    with py.test.raises(subprocess.CalledProcessError):
        db.run(["upgrade"])

    admin.sa.purge_vm_instance(vm_instance2)

    db.run(["upgrade"])
