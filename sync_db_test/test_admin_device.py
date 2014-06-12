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

import py.test

import sync_db.error

import raises

def test_add_device_invalid(admin):
    with raises.sync_error(sync_db.error.DEVICE_NAME_REQUIRED):
        admin.sa.add_device(None)

    with raises.sync_error(sync_db.error.DEVICE_NAME_TOO_LONG):
        admin.sa.add_device("x" * 201)

def test_complete_device_uuid(admin):
    device1 = admin.sa.add_device("name1")
    device2 = admin.sa.add_device("name2")

    devices = sorted([device1, device2])

    assert admin.sa.complete_device_uuid("") == devices
    assert admin.sa.complete_device_uuid(device1) == [device1]
    assert admin.sa.complete_device_uuid("x") == []

    admin.sa.remove_device(device1)
    assert admin.sa.complete_device_uuid("") == [device2]

def test_get_device(admin):
    device1 = admin.sa.add_device("name1")
    device2 = admin.sa.add_device("name2")

    assert admin.sa.get_device(device1) == (device1, "name1", None)
    assert admin.sa.get_device(device2) == (device2, "name2", None)

    with raises.sync_error(sync_db.error.DEVICE_NOT_FOUND):
        admin.sa.get_device("unknown")

    with raises.sync_error(sync_db.error.DEVICE_NOT_FOUND):
        admin.sa.get_device_secret("unknown")

    secret1 = admin.sa.get_device_secret(device1)
    assert admin.sa.get_device_secret(device2) != secret1

    admin.sa.reset_device_secret(device1)
    assert admin.sa.get_device_secret(device1) != secret1

    admin.sa.remove_device(device1)

    with raises.sync_error(sync_db.error.DEVICE_NOT_FOUND):
        admin.sa.get_device(device1)

    with raises.sync_error(sync_db.error.DEVICE_NOT_FOUND):
        admin.sa.get_device_secret(device1)

def test_device_config(admin):
    device1 = admin.sa.add_device("name1", config=["a:b:c"])
    assert admin.sa.get_device_config(device1) == [("a", "b", "c")]

    device2 = admin.sa.add_device("name1", config=["a:b:c", "d:e:f"])
    assert admin.sa.get_device_config(device2) == [("a", "b", "c"),
                                                ("d", "e", "f")]

    device3 = admin.sa.add_device("name1", config=["a:b:c", "a:e:f"])
    assert admin.sa.get_device_config(device3) == [("a", "b", "c"),
                                                ("a", "e", "f")]

    device4 = admin.sa.add_device("name1", config=["a:b:c", "d:b:f"])
    assert admin.sa.get_device_config(device4) == [("a", "b", "c"),
                                                ("d", "b", "f")]

    device5 = admin.sa.add_device("name1", config=["a:b:c", "a:b:f"])
    assert admin.sa.get_device_config(device5) == [("a", "b", "f")]

    device6 = admin.sa.add_device("name1", config=["a:b:"])
    assert admin.sa.get_device_config(device6) == []

    device7 = admin.sa.add_device("name1", config=["a:b:c", "a:b:"])
    assert admin.sa.get_device_config(device7) == []

    admin.sa.modify_device_config(device1, [])
    assert admin.sa.get_device_config(device1) == [("a", "b", "c")]

    admin.sa.modify_device_config(device1, ["d:e:f"])
    assert admin.sa.get_device_config(device1) == [("a", "b", "c"),
                                                ("d", "e", "f")]

    admin.sa.modify_device_config(device1, ["d:e:"])
    assert admin.sa.get_device_config(device1) == [("a", "b", "c")]

    admin.sa.modify_device_config(device1, ["d:e:f"], replace=True)
    assert admin.sa.get_device_config(device1) == [("d", "e", "f")]

    device8 = admin.sa.add_device("name1", config=["a" * 100 + ":" +
                                                   "b" * 100 + ":" +
                                                   "c" * 3500])
    assert admin.sa.get_device_config(device8) == [("a" * 100,
                                                    "b" * 100,
                                                    "c" * 3500)]

def test_device_config_invalid(admin):
    device = admin.sa.add_device("name1")

    with raises.sync_error(sync_db.error.CONFIG_EMPTY):
        admin.sa.add_device("name2", config=[""])

    with raises.sync_error(sync_db.error.CONFIG_EMPTY):
        admin.sa.modify_device_config(device, [""])

    with raises.sync_error(sync_db.error.CONFIG_INVALID):
        admin.sa.add_device("name2", config=[":b:c"])

    with raises.sync_error(sync_db.error.CONFIG_INVALID):
        admin.sa.modify_device_config(device, [":b:c"])

    with raises.sync_error(sync_db.error.CONFIG_DAEMON_TOO_LONG):
        admin.sa.add_device("name2", config=["a" * 101 + ":b:c"])

    with raises.sync_error(sync_db.error.CONFIG_DAEMON_TOO_LONG):
        admin.sa.modify_device_config(device, ["a" * 101 + ":b:c"])

    with raises.sync_error(sync_db.error.CONFIG_KEY_TOO_LONG):
        admin.sa.add_device("name2", config=["a:" + "b" * 101 + ":c"])

    with raises.sync_error(sync_db.error.CONFIG_KEY_TOO_LONG):
        admin.sa.modify_device_config(device, ["a:" + "b" * 101 + ":c"])

    with raises.sync_error(sync_db.error.CONFIG_VALUE_TOO_LONG):
        admin.sa.add_device("name2", config=["a:b:" + "c" * 3501])

    with raises.sync_error(sync_db.error.CONFIG_VALUE_TOO_LONG):
        admin.sa.modify_device_config(device, ["a:b:" + "c" * 3501])

def test_device_repo(admin):
    repo = admin.sa.add_repo("release", "build", "path", 1, "1" * 64)

    device = admin.sa.add_device("name", repo_uuid=repo)

    with raises.sync_error(sync_db.error.REPO_NOT_FOUND):
        admin.sa.add_device("name", repo_uuid="unknown")

    with raises.sync_error(sync_db.error.REPO_NOT_FOUND):
        admin.sa.add_device("name", repo_uuid="x" * 37)

    admin.sa.modify_device_repo(device, None)
    admin.sa.modify_device_repo(device, repo)

    with raises.sync_error(sync_db.error.REPO_NOT_FOUND):
        admin.sa.modify_device_repo(device, repo_uuid="unknown")

    with raises.sync_error(sync_db.error.REPO_NOT_FOUND):
        admin.sa.modify_device_repo(device, repo_uuid="x" * 37)

def test_list_devices(admin):
    device1 = admin.sa.add_device("name1")
    device2 = admin.sa.add_device("name2")

    device1_row = (device1, "name1")
    device2_row = (device2, "name2")

    with raises.sync_error(sync_db.error.MULTIPLE_FILTERS):
        admin.sa.list_devices(device_name="name1", repo_uuid="dummy")

    assert admin.sa.list_devices() == sorted([device1_row, device2_row])

    assert admin.sa.list_devices(device_name="unknown") == []
    assert admin.sa.list_devices(device_name="name1") == [device1_row]

    admin.sa.remove_device(device1)
    assert admin.sa.list_devices() == [device2_row]

def test_list_devices_by_repo(admin):
    repo = admin.sa.add_repo("release", "build", "path", 1, "1" * 64)

    device1 = admin.sa.add_device("name1", repo_uuid=repo)
    device2 = admin.sa.add_device("name2")

    device1_row = (device1, "name1")
    device2_row = (device2, "name2")

    assert admin.sa.list_devices(repo_uuid=repo) == [device1_row]
    assert admin.sa.list_devices(no_repo=True) == [device2_row]

    with raises.sync_error(sync_db.error.REPO_NOT_FOUND):
        assert admin.sa.list_devices(repo_uuid="unknown") == []

def test_list_devices_by_vm(admin):
    device1 = admin.sa.add_device("name1")
    device2 = admin.sa.add_device("name2")

    device1_row = (device1, "name1")

    vm = admin.sa.add_vm("name", [])
    vm_instance = admin.sa.add_vm_instance(device1, vm, "name")

    assert admin.sa.list_devices(vm_uuid=vm) == [device1_row]
    #assert admin.sa.list_devices(vm_uuid=vm, removed=True) == []

    admin.sa.remove_vm_instance(vm_instance, True)
    assert admin.sa.list_devices(vm_uuid=vm) == []
    #assert admin.sa.list_devices(vm_uuid=vm, removed=True) == [device1_row]

    admin.sa.readd_vm_instance(vm_instance)
    assert admin.sa.list_devices(vm_uuid=vm) == [device1_row]
    #assert admin.sa.list_devices(vm_uuid=vm, removed=True) == []

    admin.sa.purge_vm_instance(vm_instance)
    assert admin.sa.list_devices(vm_uuid=vm) == []
    #assert admin.sa.list_devices(vm_uuid=vm, removed=True) == []

    vm_instance = admin.sa.add_vm_instance(device1, vm, "name")

    admin.sa.remove_device(device1, cascade=True)
    assert admin.sa.list_devices(vm_uuid=vm) == []
    #assert admin.sa.list_devices(vm_uuid=vm, removed=True) == []

    with raises.sync_error(sync_db.error.VM_NOT_FOUND):
        assert admin.sa.list_devices(vm_uuid="unknown") == []

def test_remove_device(admin):
    device1 = admin.sa.add_device("name1")
    device2 = admin.sa.add_device("name2")
    admin.sa.verify_database()

    with raises.sync_error(sync_db.error.DEVICE_NOT_FOUND):
        admin.sa.remove_device("unknown")

    admin.sa.remove_device(device1)
    admin.sa.verify_database()

    with raises.sync_error(sync_db.error.DEVICE_NOT_FOUND):
        admin.sa.remove_device(device1)

    vm = admin.sa.add_vm("name", [])
    vm_instance1 = admin.sa.add_vm_instance(device2, vm, "name1")

    with raises.sync_error(sync_db.error.DEVICE_HAS_VM_INST):
        admin.sa.remove_device(device2)

    admin.sa.remove_vm_instance(vm_instance1, True)
    admin.sa.remove_device(device2)
    admin.sa.verify_database()

    device3 = admin.sa.add_device("name3")
    vm_instance2 = admin.sa.add_vm_instance(device3, vm, "name2")
    admin.sa.remove_device(device3, cascade=True)
    admin.sa.verify_database()

def test_remove_device_with_vm_instance(admin):
    device = admin.sa.add_device("name")
    vm = admin.sa.add_vm("name", [])

    vm_instance = admin.sa.add_vm_instance(device, vm, "name")
    admin.sa.verify_database()
    with raises.sync_error(sync_db.error.DEVICE_HAS_VM_INST):
        admin.sa.remove_device(device)

    admin.sa.remove_device(device, cascade=True)
    admin.sa.verify_database()

def test_get_report_invalid(admin):
    device = admin.sa.add_device("name")

    with raises.sync_error(sync_db.error.DEVICE_REQUIRED):
        admin.sa.get_report(None)

    with raises.sync_error(sync_db.error.DEVICE_NOT_FOUND):
        admin.sa.get_report("unknown")
