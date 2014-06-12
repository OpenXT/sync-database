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

def test_add_vm_instance_invalid(admin):
    vm = admin.sa.add_vm("name", [])
    device = admin.sa.add_device("name")

    with raises.sync_error(sync_db.error.DEVICE_REQUIRED):
        admin.sa.add_vm_instance(None, vm, "name")

    with raises.sync_error(sync_db.error.DEVICE_NOT_FOUND):
        admin.sa.add_vm_instance("unknown", vm, "name")

    with raises.sync_error(sync_db.error.VM_REQUIRED):
        admin.sa.add_vm_instance(device, None, "name")

    with raises.sync_error(sync_db.error.VM_NOT_FOUND):
        admin.sa.add_vm_instance(device, "unknown", "name")

    with raises.sync_error(sync_db.error.VM_INST_NAME_REQUIRED):
        admin.sa.add_vm_instance(device, vm, None)

    with raises.sync_error(sync_db.error.VM_INST_NAME_TOO_LONG):
        admin.sa.add_vm_instance(device, vm, "x" * 201)

def test_add_vm_instance_duplicate(admin):
    vm = admin.sa.add_vm("name", [])
    device = admin.sa.add_device("name")
    admin.sa.add_vm_instance(device, vm, "name")

    with raises.sync_error(sync_db.error.VM_INST_EXISTS):
        admin.sa.add_vm_instance(device, vm, "name")

def test_complete_vm_instance_uuid(admin):
    vm1 = admin.sa.add_vm("name1", [])
    vm2 = admin.sa.add_vm("name2", [])
    device = admin.sa.add_device("name1")

    vm_instance1 = admin.sa.add_vm_instance(device, vm1, "name1")
    vm_instance2 = admin.sa.add_vm_instance(device, vm2, "name2")

    vm_instances = sorted([vm_instance1, vm_instance2])

    assert admin.sa.complete_vm_instance_uuid("") == vm_instances
    assert admin.sa.complete_vm_instance_uuid(vm_instance1) == [vm_instance1]
    assert admin.sa.complete_vm_instance_uuid("x") == []

    admin.sa.remove_vm_instance(vm_instance1, True)
    assert admin.sa.complete_vm_instance_uuid("") == [vm_instance2]
    assert admin.sa.complete_vm_instance_uuid(
               "", include_removed=True) == vm_instances
    assert admin.sa.complete_vm_instance_uuid(
               "", include_unremoved=False) == []
    assert admin.sa.complete_vm_instance_uuid(
               "", include_unremoved=False,
               include_removed=True) == [vm_instance1]

    admin.sa.purge_vm_instance(vm_instance1)
    assert admin.sa.complete_vm_instance_uuid(
               "", include_removed=True) == [vm_instance2]

def test_get_vm_instance(admin):
    vm1 = admin.sa.add_vm("name1", [])
    vm2 = admin.sa.add_vm("name2", [])
    device = admin.sa.add_device("name1")

    vm_instance1 = admin.sa.add_vm_instance(device, vm1, "name1")
    vm_instance2 = admin.sa.add_vm_instance(device, vm2, "name2")
    admin.sa.lock_vm_instance(vm_instance2)

    vm_instance1_row = (vm_instance1, device, vm1, "name1", "f")
    vm_instance2_row = (vm_instance2, device, vm2, "name2", "t")

    assert (admin.sa.get_vm_instance(vm_instance1) ==
            vm_instance1_row + ("f", None))
    assert (admin.sa.get_vm_instance(vm_instance2) ==
            vm_instance2_row + ("f", None))

    with raises.sync_error(sync_db.error.VM_INST_NOT_FOUND):
        admin.sa.get_vm_instance("unknown")

    admin.sa.remove_vm_instance(vm_instance1, False)
    assert (admin.sa.get_vm_instance(vm_instance1) ==
            vm_instance1_row + ("t", "f"))

    admin.sa.readd_vm_instance(vm_instance1)
    assert (admin.sa.get_vm_instance(vm_instance1) ==
            vm_instance1_row + ("f", None))

    admin.sa.remove_vm_instance(vm_instance1, True)
    assert (admin.sa.get_vm_instance(vm_instance1) ==
            vm_instance1_row + ("t", "t"))

    admin.sa.readd_vm_instance(vm_instance1)
    assert (admin.sa.get_vm_instance(vm_instance1) ==
            vm_instance1_row + ("f", None))

    admin.sa.purge_vm_instance(vm_instance1)
    with raises.sync_error(sync_db.error.VM_INST_NOT_FOUND):
        admin.sa.get_vm_instance(vm_instance1)

def test_list_vm_instances(admin):
    vm1 = admin.sa.add_vm("name1", [])
    vm2 = admin.sa.add_vm("name2", [])
    device = admin.sa.add_device("name1")

    vm_instance1 = admin.sa.add_vm_instance(device, vm1, "name1")
    vm_instance2 = admin.sa.add_vm_instance(device, vm2, "name2")
    admin.sa.lock_vm_instance(vm_instance2)

    vm_instance1_row = (vm_instance1, device, vm1, "name1", "f")
    vm_instance2_row = (vm_instance2, device, vm2, "name2", "t")

    with raises.sync_error(sync_db.error.MULTIPLE_FILTERS):
        admin.sa.list_vm_instances(vm_instance_name="name1",
                                   device_uuid="dummy")

    assert admin.sa.list_vm_instances() == sorted([vm_instance1_row,
                                                vm_instance2_row])

    assert admin.sa.list_vm_instances(vm_instance_name="unknown") == []
    assert (admin.sa.list_vm_instances(vm_instance_name="name1") ==
            [vm_instance1_row])

    assert admin.sa.list_vm_instances(removed=True) == []
    assert admin.sa.list_vm_instances(vm_instance_name="unknown",
                                   removed=True) == []
    assert admin.sa.list_vm_instances(vm_instance_name="name1",
                                   removed=True) == []

    admin.sa.remove_vm_instance(vm_instance1, True)
    assert admin.sa.list_vm_instances() == [vm_instance2_row]
    assert admin.sa.list_vm_instances(removed=True) == [vm_instance1_row]
    assert admin.sa.list_vm_instances(vm_instance_name="name1") == []
    assert admin.sa.list_vm_instances(vm_instance_name="name1",
                                   removed=True) == [vm_instance1_row]

    admin.sa.readd_vm_instance(vm_instance1)
    assert admin.sa.list_vm_instances() == sorted([vm_instance1_row,
                                                vm_instance2_row])
    assert admin.sa.list_vm_instances(removed=True) == []

    admin.sa.purge_vm_instance(vm_instance1)
    assert admin.sa.list_vm_instances() == [vm_instance2_row]
    assert admin.sa.list_vm_instances(removed=True) == []

def test_list_vm_instances_by_vm(admin):
    vm1 = admin.sa.add_vm("name1", [])
    vm2 = admin.sa.add_vm("name2", [])
    device = admin.sa.add_device("name")

    vm_instance1 = admin.sa.add_vm_instance(device, vm1, "name1")
    vm_instance2 = admin.sa.add_vm_instance(device, vm2, "name2")
    admin.sa.lock_vm_instance(vm_instance2)

    vm_instance1_row = (vm_instance1, device, vm1, "name1", "f")

    assert admin.sa.list_vm_instances(vm_uuid=vm1) == [vm_instance1_row]
    assert admin.sa.list_vm_instances(vm_uuid=vm1, removed=True) == []

    admin.sa.remove_vm_instance(vm_instance1, True)
    assert admin.sa.list_vm_instances(vm_uuid=vm1) == []
    assert admin.sa.list_vm_instances(vm_uuid=vm1,
                                   removed=True) == [vm_instance1_row]

    admin.sa.readd_vm_instance(vm_instance1)
    assert admin.sa.list_vm_instances(vm_uuid=vm1) == [vm_instance1_row]
    assert admin.sa.list_vm_instances(vm_uuid=vm1, removed=True) == []

    admin.sa.purge_vm_instance(vm_instance1)
    assert admin.sa.list_vm_instances(vm_uuid=vm1) == []
    assert admin.sa.list_vm_instances(vm_uuid=vm1, removed=True) == []

    with raises.sync_error(sync_db.error.VM_NOT_FOUND):
        assert admin.sa.list_vm_instances(vm_uuid="unknown") == []

def test_list_vm_instances_by_device(admin):
    vm = admin.sa.add_vm("name", [])
    device1 = admin.sa.add_device("name1")
    device2 = admin.sa.add_device("name2")

    vm_instance1 = admin.sa.add_vm_instance(device1, vm, "name1")
    vm_instance2 = admin.sa.add_vm_instance(device2, vm, "name2")
    admin.sa.lock_vm_instance(vm_instance2)

    vm_instance1_row = (vm_instance1, device1, vm, "name1", "f")

    assert admin.sa.list_vm_instances(
               device_uuid=device1) == [vm_instance1_row]
    assert admin.sa.list_vm_instances(device_uuid=device1, removed=True) == []

    admin.sa.remove_vm_instance(vm_instance1, True)
    assert admin.sa.list_vm_instances(device_uuid=device1) == []
    assert admin.sa.list_vm_instances(device_uuid=device1,
                                   removed=True) == [vm_instance1_row]

    admin.sa.readd_vm_instance(vm_instance1)
    assert admin.sa.list_vm_instances(
               device_uuid=device1) == [vm_instance1_row]
    assert admin.sa.list_vm_instances(device_uuid=device1, removed=True) == []

    admin.sa.purge_vm_instance(vm_instance1)
    assert admin.sa.list_vm_instances(device_uuid=device1) == []
    assert admin.sa.list_vm_instances(device_uuid=device1, removed=True) == []

    with raises.sync_error(sync_db.error.DEVICE_NOT_FOUND):
        assert admin.sa.list_vm_instances(device_uuid="unknown") == []

def test_list_vm_instances_by_disk(admin):
    disk = admin.sa.add_disk("name", "v", "path", 0, "0" * 64, None, False,
                             False)
    vm1 = admin.sa.add_vm("name1", [disk])
    vm2 = admin.sa.add_vm("name2", [])
    device = admin.sa.add_device("name")

    vm_instance1 = admin.sa.add_vm_instance(device, vm1, "name1")
    vm_instance2 = admin.sa.add_vm_instance(device, vm2, "name2")
    admin.sa.lock_vm_instance(vm_instance2)

    vm_instance1_row = (vm_instance1, device, vm1, "name1", "f")

    assert admin.sa.list_vm_instances(disk_uuid=disk) == [vm_instance1_row]
    assert admin.sa.list_vm_instances(disk_uuid=disk, removed=True) == []

    admin.sa.remove_vm_instance(vm_instance1, True)
    assert admin.sa.list_vm_instances(disk_uuid=disk) == []
    assert admin.sa.list_vm_instances(disk_uuid=disk,
                                   removed=True) == [vm_instance1_row]

    admin.sa.readd_vm_instance(vm_instance1)
    assert admin.sa.list_vm_instances(disk_uuid=disk) == [vm_instance1_row]
    assert admin.sa.list_vm_instances(disk_uuid=disk, removed=True) == []

    admin.sa.purge_vm_instance(vm_instance1)
    assert admin.sa.list_vm_instances(disk_uuid=disk) == []
    assert admin.sa.list_vm_instances(disk_uuid=disk, removed=True) == []

    with raises.sync_error(sync_db.error.DISK_NOT_FOUND):
        assert admin.sa.list_vm_instances(disk_uuid="unknown") == []

def test_lock_vm_instance(admin):
    vm = admin.sa.add_vm("name", [])
    device = admin.sa.add_device("name")

    vm_instance = admin.sa.add_vm_instance(device, vm, "name")

    with raises.sync_error(sync_db.error.VM_INST_ALREADY_UNLOCKED):
        admin.sa.unlock_vm_instance(vm_instance)

    admin.sa.lock_vm_instance(vm_instance)

    with raises.sync_error(sync_db.error.VM_INST_ALREADY_LOCKED):
        admin.sa.lock_vm_instance(vm_instance)

    admin.sa.unlock_vm_instance(vm_instance)

    assert (admin.sa.get_vm_instance(vm_instance) ==
            (vm_instance, device, vm, "name", "f", "f", None))

def test_modify_vm_instance_name(admin):
    vm = admin.sa.add_vm("name1", [])
    device = admin.sa.add_device("name1")
    vm_instance = admin.sa.add_vm_instance(device, vm, "name1")
    assert (admin.sa.get_vm_instance(vm_instance) ==
            (vm_instance, device, vm, "name1", "f", "f", None))

    admin.sa.modify_vm_instance_name(vm_instance, "name2")
    assert (admin.sa.get_vm_instance(vm_instance) ==
            (vm_instance, device, vm, "name2", "f", "f", None))

    with raises.sync_error(sync_db.error.VM_INST_NAME_REQUIRED):
        admin.sa.modify_vm_instance_name(vm_instance, None)

    with raises.sync_error(sync_db.error.VM_INST_NAME_TOO_LONG):
        admin.sa.modify_vm_instance_name(vm_instance, "x" * 201)

def test_remove_vm_instance(admin):
    vm1 = admin.sa.add_vm("name1", [])
    vm2 = admin.sa.add_vm("name2", [])
    device = admin.sa.add_device("name1")

    vm_instance1 = admin.sa.add_vm_instance(device, vm1, "name1")
    vm_instance2 = admin.sa.add_vm_instance(device, vm2, "name2")
    admin.sa.verify_database()

    admin.sa.remove_vm_instance(vm_instance1, True)
    admin.sa.verify_database()
    with raises.sync_error(sync_db.error.VM_INST_ALREADY_REMOVED):
        admin.sa.remove_vm_instance(vm_instance1, True)

    admin.sa.readd_vm_instance(vm_instance1)
    admin.sa.verify_database()
    with raises.sync_error(sync_db.error.VM_INST_NOT_REMOVED):
        admin.sa.readd_vm_instance(vm_instance1)

    admin.sa.purge_vm_instance(vm_instance1)
    admin.sa.verify_database()

    admin.sa.purge_vm_instance(vm_instance2)
    admin.sa.verify_database()

    with raises.sync_error(sync_db.error.VM_INST_NOT_FOUND):
        admin.sa.remove_vm_instance(vm_instance1, True)

    with raises.sync_error(sync_db.error.VM_INST_NOT_FOUND):
        admin.sa.readd_vm_instance(vm_instance1)

    with raises.sync_error(sync_db.error.VM_INST_NOT_FOUND):
        admin.sa.purge_vm_instance(vm_instance1)

def test_remove_vm_instance_invalid(admin):
    with raises.sync_error(sync_db.error.VM_INST_NOT_FOUND):
        admin.sa.remove_vm_instance("unknown", True)

    with raises.sync_error(sync_db.error.VM_INST_NOT_FOUND):
        admin.sa.readd_vm_instance("unknown")

    with raises.sync_error(sync_db.error.VM_INST_NOT_FOUND):
        admin.sa.purge_vm_instance("unknown")
