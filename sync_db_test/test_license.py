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

import datetime
import py.test

import sync_db.error

import raises

def test_license_online(clean_db):
    past = datetime.datetime(1900, 1, 1, 0, 0)
    future = datetime.datetime(3000, 1, 1, 0, 0)

    admin = clean_db.get_admin_connection()
    server = clean_db.get_server_connection()
    license = clean_db.get_license_connection()

    devices = sorted([admin.sa.add_device("name{0}".format(i))
                      for i in range(0, 5)])

    # All devices: unlicensed.

    assert license.sl.lock_next_requested_license(None) is None
    assert license.sl.lock_next_expired_license(None) is None

    for i in range(1, 5):
        server.ss.get_device_state(devices[i])

    # Device 0: unlicensed.
    # Devices 1 to 4: requested.

    assert license.sl.lock_next_requested_license(None) == devices[1]
    license.sl.deny_requested_license(devices[1])

    assert license.sl.lock_next_requested_license(devices[1]) == devices[2]
    license.sl.grant_requested_license(devices[2], future, "hash")

    assert license.sl.lock_next_requested_license(devices[2]) == devices[3]
    license.sl.grant_requested_license(devices[3], past, "hash")

    assert license.sl.lock_next_requested_license(devices[3]) == devices[4]
    license.sl.grant_requested_license(devices[4], past, "hash")

    assert license.sl.lock_next_requested_license(devices[4]) is None

    assert license.sl.lock_next_expired_license(None) is None

    # Device 0 and 1: unlicensed.
    # Device 2: granted with far future expiry date.
    # Devices 3 and 4: granted with past expiry date.

    for i in range(2, 5):
        server.ss.get_device_state(devices[i])

    # Device 0 and 1: unlicensed.
    # Device 2: granted with far future expiry date.
    # Devices 3 and 4: expired.

    assert license.sl.lock_next_requested_license(None) is None

    assert license.sl.lock_next_expired_license(None) == devices[3]
    license.sl.skip_expired_license()

    assert license.sl.lock_next_expired_license(devices[3]) == devices[4]
    license.sl.revoke_expired_license(devices[4])

    assert license.sl.lock_next_expired_license(devices[4]) is None

    # Device 0 and 1: unlicensed.
    # Device 2: granted with far future expiry date.
    # Device 3: expired.
    # Device 4: unlicensed.

    assert license.sl.lock_next_requested_license(None) is None

    assert license.sl.lock_next_expired_license(None) == devices[3]
    license.sl.skip_expired_license()

    assert license.sl.lock_next_expired_license(devices[3]) is None

    license.sl.revoke_all_licenses()

    # Device 0 and 1: unlicensed.
    # Device 2: requested.
    # Devices 3 and 4: unlicensed.

    assert license.sl.lock_next_requested_license(None) == devices[2]
    license.sl.deny_requested_license(devices[2])

    assert license.sl.lock_next_requested_license(devices[2]) is None

    assert license.sl.lock_next_expired_license(None) is None

    # All devices: unlicensed.

    assert license.sl.lock_next_requested_license(None) is None

    assert license.sl.lock_next_expired_license(None) is None

def test_license_random(clean_db):
    future = datetime.datetime(3000, 1, 1, 0, 0)

    admin = clean_db.get_admin_connection()
    server = clean_db.get_server_connection()
    license = clean_db.get_license_connection()

    devices = sorted([admin.sa.add_device("name{0}".format(i))
                      for i in range(0, 10)])

    # All devices: unlicensed.

    license.sl.expire_random_licenses()

    for i in range(0, 10):
        server.ss.get_device_state(devices[i])

    license.sl.expire_random_licenses()

    # All devices: requested.

    for i in range(0, 10):
        prev_device = devices[i - 1] if i > 0 else None
        assert license.sl.lock_next_requested_license(
                   prev_device) == devices[i]
        license.sl.grant_requested_license(devices[i], future, "hash")

    license.sl.expire_random_licenses()

    # Zero or more devices: expired. Not much we can do to test this.

def test_license_online_target_state(clean_db):
    past = datetime.datetime(1900, 1, 1, 0, 0)

    admin = clean_db.get_admin_connection()
    server = clean_db.get_server_connection()
    license = clean_db.get_license_connection()

    device = admin.sa.add_device("name")
    get_device_state_check(server, device, None, None, "t")

    assert license.sl.lock_next_requested_license(None) == device
    license.sl.deny_requested_license(device)
    get_device_state_check(server, device, None, None, "t")

    assert license.sl.lock_next_requested_license(None) == device
    license.sl.grant_requested_license(device, past, "hash")
    get_device_state_check(server, device, past, "hash", "t")

    assert license.sl.lock_next_expired_license(None) == device
    license.sl.skip_expired_license()
    get_device_state_check(server, device, past, "hash", "t")

    assert license.sl.lock_next_expired_license(None) == device
    license.sl.revoke_expired_license(device)
    get_device_state_check(server, device, past, "hash", "t")

def test_license_mode(clean_db):
    admin = clean_db.get_admin_connection()
    server = clean_db.get_server_connection()
    license = clean_db.get_license_connection()

    assert admin.sa.get_licensing() == ("online", None, 0)

    device = admin.sa.add_device("name")
    assert admin.sa.get_licensing() == ("online", None, 1)

    server.ss.get_device_state(device)
    assert license.sl.lock_next_requested_license(None) == device
    license.sl.deny_requested_license(device)

    license.sl.set_num_offline_licenses(1)
    assert admin.sa.get_licensing() == ("offline", 1, 1)

    license.sl.set_num_offline_licenses(None)
    assert admin.sa.get_licensing() == ("online", None, 1)
    assert license.sl.lock_next_requested_license(None) is None

    license.sl.set_num_offline_licenses(0)
    assert admin.sa.get_licensing() == ("offline", 0, 1)

    with raises.sync_error(sync_db.error.NUM_LICENSES_INVALID):
        license.sl.set_num_offline_licenses(-1)

    with raises.sync_error(sync_db.error.NUM_LICENSES_INVALID):
        license.sl.set_num_offline_licenses(1e10)

def test_license_mode_check(license):
    license.sl.set_num_offline_licenses(1)

    with raises.sync_error(sync_db.error.OFFLINE_LICENSING):
        license.sl.deny_requested_license(None)

    with raises.sync_error(sync_db.error.OFFLINE_LICENSING):
        license.sl.expire_random_licenses()

    with raises.sync_error(sync_db.error.OFFLINE_LICENSING):
        license.sl.grant_requested_license(None, None, None)

    with raises.sync_error(sync_db.error.OFFLINE_LICENSING):
        license.sl.lock_next_expired_license(None)

    with raises.sync_error(sync_db.error.OFFLINE_LICENSING):
        license.sl.lock_next_requested_license(None)

    with raises.sync_error(sync_db.error.OFFLINE_LICENSING):
        license.sl.revoke_all_licenses()

    with raises.sync_error(sync_db.error.OFFLINE_LICENSING):
        license.sl.revoke_expired_license(None)

    with raises.sync_error(sync_db.error.OFFLINE_LICENSING):
        license.sl.skip_expired_license()

def test_license_offline_target_state(clean_db):
    past = datetime.datetime(1900, 1, 1, 0, 0)

    admin = clean_db.get_admin_connection()
    server = clean_db.get_server_connection()
    license = clean_db.get_license_connection()

    device = admin.sa.add_device("name")
    get_device_state_check(server, device, None, None, "t")

    license.sl.set_num_offline_licenses(1)
    get_device_state_check(server, device, None, None, "f")

    license.sl.set_num_offline_licenses(None)
    get_device_state_check(server, device, None, None, "t")

    assert license.sl.lock_next_requested_license(None) == device
    license.sl.grant_requested_license(device, past, "hash")
    get_device_state_check(server, device, past, "hash", "t")

    license.sl.set_num_offline_licenses(1)
    get_device_state_check(server, device, None, None, "f")

    license.sl.set_num_offline_licenses(None)
    get_device_state_check(server, device, None, None, "t")

def test_license_offline_enforcement(clean_db):
    admin = clean_db.get_admin_connection()
    license = clean_db.get_license_connection()

    license.sl.set_num_offline_licenses(5)

    devices = [admin.sa.add_device("name{0}".format(i))
               for i in range(0, 5)]

    with raises.sync_error(sync_db.error.OUT_OF_LICENSES):
        admin.sa.add_device("name5")

    admin.sa.remove_device(devices.pop())
    devices.append(admin.sa.add_device("name4"))

    with raises.sync_error(sync_db.error.OUT_OF_LICENSES):
        admin.sa.add_device("name5")

    license.sl.set_num_offline_licenses(10)

    devices.extend([admin.sa.add_device("name{0}".format(i))
                    for i in range(5, 10)])

    with raises.sync_error(sync_db.error.OUT_OF_LICENSES):
        admin.sa.add_device("name10")

    license.sl.set_num_offline_licenses(5)
    license.sl.set_num_offline_licenses(None)
    devices.append(admin.sa.add_device("name10"))

def get_device_state_check(server, device, expected_expiry_time,
                           expected_hash, expected_online):
    device_info, _, _, _, _, _ = server.ss.get_device_state(device)
    _, _, _, _, _, license_expiry_time, license_hash, online = device_info

    if license_expiry_time is not None:
        license_expiry_date = license_expiry_time.split()[0]
    else:
        license_expiry_date = None

    if expected_expiry_time is not None:
        expected_expiry_date = expected_expiry_time.strftime("%Y-%m-%d")
    else:
        expected_expiry_date = None

    assert license_expiry_date == expected_expiry_date
    assert license_hash == expected_hash
    assert online == expected_online
