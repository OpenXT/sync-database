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

def test_add_disk_invalid(admin):
    with raises.sync_error(sync_db.error.DISK_NAME_REQUIRED):
        admin.sa.add_disk(None, "v", "path", -1, "0" * 64, None, False, False)

    with raises.sync_error(sync_db.error.DISK_NAME_TOO_LONG):
        admin.sa.add_disk("x" * 201, "v", "path", -1, "0" * 64, None, False,
                          False)

    with raises.sync_error(sync_db.error.FILE_PATH_REQUIRED):
        admin.sa.add_disk("name", "v", None, -1, "0" * 64, None, False, False)

    with raises.sync_error(sync_db.error.FILE_PATH_TOO_LONG):
        admin.sa.add_disk("name", "v", "x" * 1025, -1, "0" * 64, None, False,
                          False)

    with raises.sync_error(sync_db.error.FILE_SIZE_REQUIRED):
        admin.sa.add_disk("name", "v", "path", None, "0" * 64, None, False,
                          False)

    with raises.sync_error(sync_db.error.FILE_SIZE_INVALID):
        admin.sa.add_disk("name", "v", "path", -1, "0" * 64, None, False,
                          False)

    with raises.sync_error(sync_db.error.FILE_SIZE_INVALID):
        admin.sa.add_disk("name", "v", "path", 1e13, "0" * 64, None, False,
                          False)

    with raises.sync_error(sync_db.error.FILE_HASH_REQUIRED):
        admin.sa.add_disk("name", "v", "path", 0, None, None, False, False)

    with raises.sync_error(sync_db.error.FILE_HASH_INVALID):
        admin.sa.add_disk("name", "v", "path", 0, "0" * 63, None, False, False)

    with raises.sync_error(sync_db.error.FILE_HASH_INVALID):
        admin.sa.add_disk("name", "v", "path", 0, "0" * 65, None, False, False)

    with raises.sync_error(sync_db.error.ENCRYPTION_KEY_INVALID):
        admin.sa.add_disk("name", "v", "path", 0, "0" * 64, "x", False, False)

    for length in 63, 65, 127, 129:
        with raises.sync_error(sync_db.error.ENCRYPTION_KEY_INVALID):
            admin.sa.add_disk("name", "v", "path", 0, "0" * 64, "0" * length,
                              False, False)

    with raises.sync_error(sync_db.error.DISK_TYPE_INVALID):
        admin.sa.add_disk("name", "x", "path", 0, "0" * 64, "x", False, False)

    with raises.sync_error(sync_db.error.ISO_WITH_ENCRYPTION_KEY):
        admin.sa.add_disk("name", "i", "path", 0, "0" * 64, "0" * 64, False,
                          True)

    with raises.sync_error(sync_db.error.ISO_NOT_READ_ONLY):
        admin.sa.add_disk("name", "i", "path", 0, "0" * 64, None, False, False)

    with raises.sync_error(sync_db.error.DISK_READ_ONLY_AND_SHARED):
        admin.sa.add_disk("name", "v", "path", 0, "0" * 64, None, True, True)

def test_add_disk_duplicate(admin):
    admin.sa.add_disk("name", "v", "path", 0, "0" * 64, None, False, False)

    with raises.sync_error(sync_db.error.FILE_PATH_NOT_UNIQUE):
        admin.sa.add_disk("name", "v", "path", 0, "0" * 64, None, False, False)

def test_complete_disk_uuid(admin):
    disk1 = admin.sa.add_disk("name1", "v", "path1", 0, "0" * 64, None, False,
                              False)
    disk2 = admin.sa.add_disk("name2", "v", "path2", 0, "0" * 64, None, False,
                              False)

    assert admin.sa.complete_disk_uuid("") == sorted([disk1, disk2])
    assert admin.sa.complete_disk_uuid(disk1) == [disk1]
    assert admin.sa.complete_disk_uuid("x") == []

def test_get_disk(admin):
    disk1 = admin.sa.add_disk("name1", "v", "path1", 1, "1" * 64, None,
                              False, False)
    disk2 = admin.sa.add_disk("name2", "v", "path2", 2, "2" * 64, "2" * 64,
                              True, False)
    disk3 = admin.sa.add_disk("name3", "v", "path3", 3, "3" * 64, "3" * 128,
                              True, False)

    assert admin.sa.get_disk(disk1) == (disk1, "name1", "v", "path1", 1,
                                        "1" * 64, "f", "f")
    assert admin.sa.get_disk(disk2) == (disk2, "name2", "v", "path2", 2,
                                        "2" * 64, "t", "f")
    assert admin.sa.get_disk(disk3) == (disk3, "name3", "v", "path3", 3,
                                        "3" * 64, "t", "f")

    with raises.sync_error(sync_db.error.DISK_NOT_FOUND):
        admin.sa.get_disk("unknown")

    assert admin.sa.get_disk_key(disk1) is None
    assert admin.sa.get_disk_key(disk2) == "2" * 64
    assert admin.sa.get_disk_key(disk3) == "3" * 128

    admin.sa.remove_disk(disk1)

    with raises.sync_error(sync_db.error.DISK_NOT_FOUND):
        admin.sa.get_disk(disk1)

    with raises.sync_error(sync_db.error.DISK_NOT_FOUND):
        admin.sa.get_disk_key(disk1)

def test_list_disks(admin):
    disk1 = admin.sa.add_disk("name1", "i", "path1", 1, "1" * 64, None,
                              False, True)
    disk2 = admin.sa.add_disk("name2", "v", "path2", 2, "2" * 64, "2" * 128,
                              True, False)

    disk1_row = (disk1, "name1", "i", "path1")
    disk2_row = (disk2, "name2", "v", "path2")

    with raises.sync_error(sync_db.error.MULTIPLE_FILTERS):
        admin.sa.list_disks(disk_name="name1", file_path="path1")

    assert admin.sa.list_disks() == sorted([disk1_row, disk2_row])

    assert admin.sa.list_disks(disk_type="i") == [disk1_row]
    assert admin.sa.list_disks(disk_type="v") == [disk2_row]

    assert admin.sa.list_disks(disk_name="unknown") == []
    assert admin.sa.list_disks(file_path="unknown") == []
    assert admin.sa.list_disks(file_hash="unknown") == []

    assert admin.sa.list_disks(disk_name="name1") == [disk1_row]
    assert admin.sa.list_disks(file_path="path1") == [disk1_row]
    assert admin.sa.list_disks(file_hash="1" * 64) == [disk1_row]

    assert admin.sa.list_disks(unused=True) == sorted([disk1_row, disk2_row])

def test_list_disks_by_vm(admin):
    disk1 = admin.sa.add_disk("name1", "v", "path1", 1, "1" * 64, None,
                              False, False)
    disk2 = admin.sa.add_disk("name2", "v", "path2", 2, "2" * 64, "2" * 128,
                              True, False)

    disk1_row = (disk1, "name1", "v", "path1")
    disk2_row = (disk2, "name2", "v", "path2")

    disks = list(reversed(sorted([disk1, disk2])))

    disk_rows = [row + (i + 1,) for (i, row) in
                 enumerate(reversed(sorted([disk1_row, disk2_row])))]

    vm1 = admin.sa.add_vm("name1", [])
    vm2 = admin.sa.add_vm("name2", [disks[0]])
    vm3 = admin.sa.add_vm("name3", disks)

    assert admin.sa.list_disks(vm_uuid=vm1) == []
    assert admin.sa.list_disks(vm_uuid=vm2) == disk_rows[:1]
    assert admin.sa.list_disks(vm_uuid=vm3) == disk_rows

    device = admin.sa.add_device("name")
    vm_instance = admin.sa.add_vm_instance(device, vm3, "name")

    assert admin.sa.list_disks(vm_instance_uuid=vm_instance) == disk_rows

    with raises.sync_error(sync_db.error.VM_NOT_FOUND):
        admin.sa.list_disks(vm_uuid="unknown") == []

    with raises.sync_error(sync_db.error.VM_INST_NOT_FOUND):
        admin.sa.list_disks(vm_instance_uuid="unknown")

    assert admin.sa.list_disks(unused=True) == []

def test_remove_disk(admin):
    disk1 = admin.sa.add_disk("name1", "v", "path1", 1, "1" * 64, None,
                              False, False)
    disk2 = admin.sa.add_disk("name2", "v", "path2", 2, "2" * 64, "2" * 128,
                              True, False)

    with raises.sync_error(sync_db.error.DISK_NOT_FOUND):
        admin.sa.remove_disk("unknown")

    vm = admin.sa.add_vm("name", [disk1])

    with raises.sync_error(sync_db.error.DISK_IN_USE):
        admin.sa.remove_disk(disk1)

    admin.sa.remove_disk(disk2)

    admin.sa.remove_vm(vm)
    admin.sa.remove_disk(disk1)

    with raises.sync_error(sync_db.error.DISK_NOT_FOUND):
        admin.sa.remove_disk(disk1)
