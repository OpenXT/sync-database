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

import operator
import py.test

import sync_db.error

import raises

def test_server_get_device_secret(clean_db):
    admin = clean_db.get_admin_connection()
    server = clean_db.get_server_connection()

    device = admin.sa.add_device("name")

    secret = admin.sa.get_device_secret(device)
    assert server.ss.get_device_secret(device) == secret

    with raises.sync_error(sync_db.error.DEVICE_REQUIRED):
        server.ss.get_device_secret(None)

    with raises.sync_error(sync_db.error.DEVICE_NOT_FOUND):
        server.ss.get_device_secret("unknown")

def test_server_get_disk_path(clean_db):
    admin = clean_db.get_admin_connection()
    server = clean_db.get_server_connection()

    disk1 = admin.sa.add_disk("name1", "v", "path1", 1, "1" * 64, None, False,
                              False)
    disk2 = admin.sa.add_disk("name2", "v", "path2", 2, "2" * 64, None, False,
                              False)
    disk3 = admin.sa.add_disk("name3", "v", "path3", 3, "3" * 64, None, False,
                              False)
    disk4 = admin.sa.add_disk("name4", "v", "path4", 4, "4" * 64, None, False,
                              False)

    vm1 = admin.sa.add_vm("name", [disk1])
    vm2 = admin.sa.add_vm("name", [disk2])
    vm3 = admin.sa.add_vm("name", [disk3])

    device1 = admin.sa.add_device("name1")
    vm_instance1 = admin.sa.add_vm_instance(device1, vm1, "name1")
    vm_instance2 = admin.sa.add_vm_instance(device1, vm2, "name2")
    vm_instance3 = admin.sa.add_vm_instance(device1, vm3, "name3")
    admin.sa.remove_vm_instance(vm_instance2, False)
    admin.sa.remove_vm_instance(vm_instance3, True)

    assert server.ss.get_disk_path(device1, disk1) == "path1"
    assert server.ss.get_disk_path(device1, disk2) == "path2"

    with raises.sync_error(sync_db.error.DISK_NOT_FOUND):
        server.ss.get_disk_path(device1, disk3)

    with raises.sync_error(sync_db.error.DISK_NOT_FOUND):
        server.ss.get_disk_path(device1, disk4)

    with raises.sync_error(sync_db.error.DISK_REQUIRED):
        server.ss.get_disk_path(device1, None)

    with raises.sync_error(sync_db.error.DISK_NOT_FOUND):
        server.ss.get_disk_path(device1, "unknown")

    with raises.sync_error(sync_db.error.DEVICE_REQUIRED):
        server.ss.get_disk_path(None, disk1)

    with raises.sync_error(sync_db.error.DEVICE_NOT_FOUND):
        server.ss.get_disk_path("unknown", disk1)

def test_server_get_repo_path(clean_db):
    admin = clean_db.get_admin_connection()
    server = clean_db.get_server_connection()

    repo = admin.sa.add_repo("release", "build", "path9", 9, "9" * 64)
    device1 = admin.sa.add_device("name1", repo_uuid=repo)
    device2 = admin.sa.add_device("name2")

    assert server.ss.get_repo_path(device1, repo) == "path9"

    with raises.sync_error(sync_db.error.REPO_NOT_FOUND):
        server.ss.get_repo_path(device1, "unknown")

    with raises.sync_error(sync_db.error.REPO_REQUIRED):
        server.ss.get_repo_path(device1, None)

    with raises.sync_error(sync_db.error.REPO_NOT_FOUND):
        server.ss.get_repo_path(device2, repo)

    with raises.sync_error(sync_db.error.DEVICE_REQUIRED):
        server.ss.get_repo_path(None, repo)

    with raises.sync_error(sync_db.error.DEVICE_NOT_FOUND):
        server.ss.get_repo_path("unknown", repo)

def test_server_get_device_state(clean_db):
    admin = clean_db.get_admin_connection()
    server = clean_db.get_server_connection()

    repo = admin.sa.add_repo("release", "build", "path9", 9, "9" * 64)

    disk1 = admin.sa.add_disk("name1", "v", "path1", 1, "1" * 64, "1" * 128,
                              False, False)
    disk2 = admin.sa.add_disk("name2", "v", "path2", 2, "2" * 64, None,
                              True, False)
    disk3 = admin.sa.add_disk("name3", "v", "path3", 3, "3" * 64, None,
                              False, True)
    disk4 = admin.sa.add_disk("name4", "i", "path4", 4, "4" * 64, None,
                              False, True)
    disk5 = admin.sa.add_disk("name5", "v", "path5", 5, "5" * 64, None,
                              False, False)

    vm1 = admin.sa.add_vm("name1", [], config=["a:b:c", "d:e:f"])
    vm2 = admin.sa.add_vm("name2", [disk1])
    vm3 = admin.sa.add_vm("name3", [disk1, disk2])
    vm4 = admin.sa.add_vm("name4", [disk1, disk2, disk3])
    vm5 = admin.sa.add_vm("name5", [disk1, disk2, disk3, disk4])

    device1 = admin.sa.add_device("name1", config=["g:h:i", "j:k:l"],
                                  repo_uuid=repo)

    vm_instance1 = admin.sa.add_vm_instance(device1, vm1, "name1")
    vm_instance2 = admin.sa.add_vm_instance(device1, vm2, "name2")
    vm_instance3 = admin.sa.add_vm_instance(device1, vm3, "name3")
    admin.sa.lock_vm_instance(vm_instance3)
    vm_instance4 = admin.sa.add_vm_instance(device1, vm4, "name4")
    admin.sa.remove_vm_instance(vm_instance4, False)
    vm_instance5 = admin.sa.add_vm_instance(device1, vm5, "name5")
    admin.sa.remove_vm_instance(vm_instance5, True)

    device2 = admin.sa.add_device("name2")
    vm_instance5 = admin.sa.add_vm_instance(device2, vm5, "name5")

    with raises.sync_error(sync_db.error.DEVICE_NOT_FOUND):
        server.ss.get_device_state("unknown")

    with raises.sync_error(sync_db.error.DEVICE_REQUIRED):
        server.ss.get_device_state(None)

    (device_info1,
     device_config1,
     vm_instances1,
     vm_instance_config1,
     vm_instance_disks1,
     disks1) = server.ss.get_device_state(device1)

    assert device_info1 == ("release", "build", repo, 9, "9" * 64, None, None,
                            "t")

    assert device_config1 == [("g", "h", "i"),
                              ("j", "k", "l")]

    assert vm_instances1 == list(sorted(
        [(vm_instance1, vm1, "name1", "f", "f"),
         (vm_instance2, vm2, "name2", "f", "f"),
         (vm_instance3, vm3, "name3", "t", "f"),
         (vm_instance4, vm4, "name4", "f", "t")]))

    assert vm_instance_config1 == [(vm_instance1, "a", "b", "c"),
                                   (vm_instance1, "d", "e", "f")]

    assert vm_instance_disks1 == list(sorted([(vm_instance2, disk1),
                                              (vm_instance3, disk1),
                                              (vm_instance3, disk2),
                                              (vm_instance4, disk1),
                                              (vm_instance4, disk2),
                                              (vm_instance4, disk3)],
                                             key=operator.itemgetter(0)))

    assert disks1 == list(sorted([
        (disk1, "name1", "v", 1, "1" * 64, "1" * 128, "f", "f"),
        (disk2, "name2", "v", 2, "2" * 64, None, "t", "f"),
        (disk3, "name3", "v", 3, "3" * 64, None, "f", "t")]))

    (device_info2,
     device_config2,
     vm_instances2,
     vm_instance_config2,
     vm_instance_disks2,
     disks2) = server.ss.get_device_state(device2)

    assert device_info2 == (None, None, None, None, None, None, None, "t")

    assert device_config2 == []

    assert vm_instances2 == list(sorted(
        [(vm_instance5, vm5, "name5", "f", "f")]))

    assert vm_instance_config2 == []

    assert vm_instance_disks2 == [(vm_instance5, disk1),
                                  (vm_instance5, disk2),
                                  (vm_instance5, disk3),
                                  (vm_instance5, disk4)]

    assert disks2 == list(sorted([
        (disk1, "name1", "v", 1, "1" * 64, "1" * 128, "f", "f"),
        (disk2, "name2", "v", 2, "2" * 64, None, "t", "f"),
        (disk3, "name3", "v", 3, "3" * 64, None, "f", "t"),
        (disk4, "name4", "i", 4, "4" * 64, None, "f", "t")]))

def test_server_report_device_state(clean_db):
    admin = clean_db.get_admin_connection()
    server = clean_db.get_server_connection()

    device = admin.sa.add_device("name")

    assert admin.sa.get_report(device) == (device, None, None, None)

    with raises.sync_error(sync_db.error.DEVICE_REQUIRED):
        server.ss.report_device_state(None, None, None)

    with raises.sync_error(sync_db.error.DEVICE_NOT_FOUND):
        server.ss.get_device_secret("unknown")

    with raises.sync_error(sync_db.error.RELEASE_TOO_LONG):
        server.ss.report_device_state(device, "x" * 101, None)

    with raises.sync_error(sync_db.error.BUILD_TOO_LONG):
        server.ss.report_device_state(device, None, "x" * 101)

    server.ss.report_device_state(device, None, None)
    result = admin.sa.get_report(device)
    assert result[0:1] + result [2:] == (device, None, None)
    assert result[1] is not None

    server.ss.report_device_state(device, "release", None)
    result = admin.sa.get_report(device)
    assert result[0:1] + result [2:] == (device, "release", None)
    assert result[1] is not None

    server.ss.report_device_state(device, None, "build")
    result = admin.sa.get_report(device)
    assert result[0:1] + result [2:] == (device, None, "build")
    assert result[1] is not None

    server.ss.report_device_state(device, "release", "build")
    result = admin.sa.get_report(device)
    assert result[0:1] + result [2:] == (device, "release", "build")
    assert result[1] is not None
