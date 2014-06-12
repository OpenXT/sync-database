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

def test_add_vm_invalid(admin):
    disk1 = admin.sa.add_disk("name1", "v", "path1", 0, "0" * 64, None, False,
                              False)
    disk2 = admin.sa.add_disk("name2", "v", "path2", 0, "0" * 64, None, False,
                              False)

    with raises.sync_error(sync_db.error.VM_NAME_REQUIRED):
        admin.sa.add_vm(None, [])

    with raises.sync_error(sync_db.error.VM_NAME_TOO_LONG):
        admin.sa.add_vm("x" * 201, [])

    with raises.sync_error(sync_db.error.DISK_REQUIRED):
        admin.sa.add_vm("name", [""])

    with raises.sync_error(sync_db.error.DISK_NOT_FOUND):
        admin.sa.add_vm("name", ["unknown"])

    with raises.sync_error(sync_db.error.DISK_NOT_FOUND):
        admin.sa.add_vm("name", ["x" * 37])

    with raises.sync_error(sync_db.error.DISK_REPEATED):
        admin.sa.add_vm("name", [disk1, disk1])

    with raises.sync_error(sync_db.error.DISK_REPEATED):
        admin.sa.add_vm("name", [disk1, disk2, disk1])

def test_complete_vm_uuid(admin):
    vm1 = admin.sa.add_vm("name1", [])
    vm2 = admin.sa.add_vm("name2", [])

    vms = sorted([vm1, vm2])

    assert admin.sa.complete_vm_uuid("") == vms
    assert admin.sa.complete_vm_uuid(vm1) == [vm1]
    assert admin.sa.complete_vm_uuid("x") == []

    admin.sa.remove_vm(vm1)
    assert admin.sa.complete_vm_uuid("") == [vm2]

def test_get_vm(admin):
    vm1 = admin.sa.add_vm("name1", [])
    vm2 = admin.sa.add_vm("name2", [])

    assert admin.sa.get_vm(vm1) == (vm1, "name1")
    assert admin.sa.get_vm(vm2) == (vm2, "name2")

    with raises.sync_error(sync_db.error.VM_NOT_FOUND):
        admin.sa.get_vm("unknown")

    admin.sa.remove_vm(vm1)
    with raises.sync_error(sync_db.error.VM_NOT_FOUND):
        admin.sa.get_vm(vm1)

def test_vm_config(admin):
    vm1 = admin.sa.add_vm("name1", [], ["a:b:c"])
    assert admin.sa.get_vm_config(vm1) == [("a", "b", "c")]

    vm2 = admin.sa.add_vm("name1", [], ["a:b:c", "d:e:f"])
    assert admin.sa.get_vm_config(vm2) == [("a", "b", "c"), ("d", "e", "f")]

    vm3 = admin.sa.add_vm("name1", [], ["a:b:c", "a:e:f"])
    assert admin.sa.get_vm_config(vm3) == [("a", "b", "c"), ("a", "e", "f")]

    vm4 = admin.sa.add_vm("name1", [], ["a:b:c", "d:b:f"])
    assert admin.sa.get_vm_config(vm4) == [("a", "b", "c"), ("d", "b", "f")]

    vm5 = admin.sa.add_vm("name1", [], ["a:b:c", "a:b:f"])
    assert admin.sa.get_vm_config(vm5) == [("a", "b", "f")]

    vm6 = admin.sa.add_vm("name1", [], ["a:b:"])
    assert admin.sa.get_vm_config(vm6) == []

    vm7 = admin.sa.add_vm("name1", [], ["a:b:c", "a:b:"])
    assert admin.sa.get_vm_config(vm7) == []

    admin.sa.modify_vm_config(vm1, [])
    assert admin.sa.get_vm_config(vm1) == [("a", "b", "c")]

    admin.sa.modify_vm_config(vm1, ["d:e:f"])
    assert admin.sa.get_vm_config(vm1) == [("a", "b", "c"),
                                           ("d", "e", "f")]

    admin.sa.modify_vm_config(vm1, ["d:e:"])
    assert admin.sa.get_vm_config(vm1) == [("a", "b", "c")]

    admin.sa.modify_vm_config(vm1, ["d:e:f"], replace=True)
    assert admin.sa.get_vm_config(vm1) == [("d", "e", "f")]

    vm8 = admin.sa.add_vm("name1", [], config=["a" * 100 + ":" +
                                               "b" * 100 + ":" +
                                               "c" * 3500])
    assert admin.sa.get_vm_config(vm8) == [("a" * 100,
                                            "b" * 100,
                                            "c" * 3500)]

def test_vm_config_invalid(admin):
    vm = admin.sa.add_vm("name1", [])

    with raises.sync_error(sync_db.error.CONFIG_EMPTY):
        admin.sa.add_vm("name2", [], [""])

    with raises.sync_error(sync_db.error.CONFIG_INVALID):
        admin.sa.add_vm("name2", [], [":b:c"])

    with raises.sync_error(sync_db.error.CONFIG_DAEMON_TOO_LONG):
        admin.sa.add_vm("name2", [], ["a" * 101 + ":b:c"])

    with raises.sync_error(sync_db.error.CONFIG_KEY_TOO_LONG):
        admin.sa.add_vm("name2", [], ["a:" + "b" * 101 + ":c"])

    with raises.sync_error(sync_db.error.CONFIG_VALUE_TOO_LONG):
        admin.sa.add_vm("name2", [], ["a:b:" + "c" * 3501])

def test_list_vms(admin):
    vm1 = admin.sa.add_vm("name1", [])
    vm2 = admin.sa.add_vm("name2", [])

    vm1_row = (vm1, "name1")
    vm2_row = (vm2, "name2")

    with raises.sync_error(sync_db.error.MULTIPLE_FILTERS):
        admin.sa.list_vms(vm_name="name1", device_uuid="dummy")

    assert admin.sa.list_vms() == sorted([vm1_row, vm2_row])

    assert admin.sa.list_vms(vm_name="unknown") == []
    assert admin.sa.list_vms(vm_name="name1") == [vm1_row]

    admin.sa.remove_vm(vm1)
    assert admin.sa.list_vms() == [vm2_row]

def test_list_vms_by_device(admin):
    vm1 = admin.sa.add_vm("name1", [])
    vm2 = admin.sa.add_vm("name2", [])

    vm1_row = (vm1, "name1")

    device = admin.sa.add_device("name")

    vm_instance = admin.sa.add_vm_instance(device, vm1, "name")
    assert admin.sa.list_vms(device_uuid=device) == [vm1_row]
    #assert admin.sa.list_vms(device_uuid=device, removed=True) == []

    admin.sa.remove_vm_instance(vm_instance, True)
    assert admin.sa.list_vms(device_uuid=device) == []
    #assert admin.sa.list_vms(device_uuid=device, removed=True) == [vm1_row]

    admin.sa.readd_vm_instance(vm_instance)
    assert admin.sa.list_vms(device_uuid=device) == [vm1_row]
    #assert admin.sa.list_vms(device_uuid=device, removed=True) == []

    admin.sa.purge_vm_instance(vm_instance)
    assert admin.sa.list_vms(device_uuid=device) == []
    #assert admin.sa.list_vms(device_uuid=device, removed=True) == []

    with raises.sync_error(sync_db.error.DEVICE_NOT_FOUND):
        assert admin.sa.list_vms(device_uuid="unknown") == []

def test_list_vms_by_disk(admin):
    disk = admin.sa.add_disk("name", "v", "path", 0, "0" * 64, None, False,
                             False)

    vm1 = admin.sa.add_vm("name1", [disk])
    vm2 = admin.sa.add_vm("name2", [])

    vm1_row = (vm1, "name1")

    assert admin.sa.list_vms(disk_uuid=disk) == [vm1_row]

    admin.sa.remove_vm(vm1)
    assert admin.sa.list_vms(disk_uuid=disk) == []

    with raises.sync_error(sync_db.error.DISK_NOT_FOUND):
        assert admin.sa.list_vms(disk_uuid="unknown") == []

def test_remove_vm(admin):
    disk = admin.sa.add_disk("name", "v", "path", 0, "0" * 64, None, False,
                             False)
    vm1 = admin.sa.add_vm("name1", [disk])
    vm2 = admin.sa.add_vm("name2", [disk])
    admin.sa.verify_database()

    with raises.sync_error(sync_db.error.VM_NOT_FOUND):
        admin.sa.remove_vm("unknown")

    admin.sa.remove_vm(vm1)
    with raises.sync_error(sync_db.error.VM_NOT_FOUND):
        admin.sa.remove_vm(vm1)

    device = admin.sa.add_device("name")
    vm_instance = admin.sa.add_vm_instance(device, vm2, "name")
    admin.sa.verify_database()

    with raises.sync_error(sync_db.error.VM_IN_USE):
        admin.sa.remove_vm(vm2)

    admin.sa.remove_vm_instance(vm_instance, True)
    admin.sa.verify_database()

    with raises.sync_error(sync_db.error.VM_IN_USE):
        admin.sa.remove_vm(vm2)

    admin.sa.purge_vm_instance(vm_instance)
    admin.sa.remove_vm(vm2)
    admin.sa.verify_database()
