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

import py.test

import sync_db.error

import raises

def test_version(clean_db):
    admin = clean_db.get_admin_connection()

    target_version = clean_db.get_target_version()
    
    assert admin.sv.get_version() == target_version

    admin.sv.check_version(target_version)

    with raises.sync_error(sync_db.error.DB_VERSION_INCOMPATIBLE):
        admin.sv.check_version("1")
