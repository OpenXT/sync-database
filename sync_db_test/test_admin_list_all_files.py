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

def test_list_all_files(admin):
    disk1 = admin.sa.add_disk("name1", "i", "path1", 1, "1" * 64, None,
                              False, True)
    disk2 = admin.sa.add_disk("name2", "v", "path2", 2, "2" * 64, "2" * 128,
                              True, False)

    disk1_row = (disk1, "path1", 1, "1" * 64)
    disk2_row = (disk2, "path2", 2, "2" * 64)

    disk_rows = sorted([disk1_row, disk2_row])

    repo1 = admin.sa.add_repo("release1", "build1", "path1", 1, "1" * 64)
    repo2 = admin.sa.add_repo("release2", "build2", "path2", 2, "2" * 64)

    repo1_row = (repo1, "path1", 1, "1" * 64)
    repo2_row = (repo2, "path2", 2, "2" * 64)

    repo_rows = sorted([repo1_row, repo2_row])

    assert admin.sa.list_all_files() == (disk_rows, repo_rows)
