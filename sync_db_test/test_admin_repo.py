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

def test_add_repo_invalid(admin):
    with raises.sync_error(sync_db.error.RELEASE_REQUIRED):
        admin.sa.add_repo(None, "build", "path", 1, "1" * 64)

    with raises.sync_error(sync_db.error.RELEASE_TOO_LONG):
        admin.sa.add_repo("x" * 101, "build", "path", 1, "1" * 64)

    with raises.sync_error(sync_db.error.BUILD_REQUIRED):
        admin.sa.add_repo("release", None, "path", 1, "1" * 64)

    with raises.sync_error(sync_db.error.BUILD_TOO_LONG):
        admin.sa.add_repo("release", "x" * 101, "path", 1, "1" * 64)

    with raises.sync_error(sync_db.error.FILE_PATH_REQUIRED):
        admin.sa.add_repo("release", "build", None, 1, "1" * 64)

    with raises.sync_error(sync_db.error.FILE_PATH_TOO_LONG):
        admin.sa.add_repo("release", "build", "x" * 1025, 1, "1" * 64)

    with raises.sync_error(sync_db.error.FILE_SIZE_REQUIRED):
        admin.sa.add_repo("release", "build", "path", None, "1" * 64)

    with raises.sync_error(sync_db.error.FILE_SIZE_INVALID):
        admin.sa.add_repo("release", "build", "path", -1, "1" * 64)

    with raises.sync_error(sync_db.error.FILE_SIZE_INVALID):
        admin.sa.add_repo("release", "build", "path", 1e13, "1" * 64)

    with raises.sync_error(sync_db.error.FILE_HASH_REQUIRED):
        admin.sa.add_repo("release", "build", "path", 1, None)

    with raises.sync_error(sync_db.error.FILE_HASH_INVALID):
        admin.sa.add_repo("release", "build", "path", 1, "1" * 63)

    with raises.sync_error(sync_db.error.FILE_HASH_INVALID):
        admin.sa.add_repo("release", "build", "path", 1, "1" * 65)

def test_add_repo_duplicate(admin):
    admin.sa.add_repo("release1", "build1", "path1", 1, "1" * 64)

    with raises.sync_error(sync_db.error.REPO_EXISTS):
        admin.sa.add_repo("release1", "build1", "path2", 2, "2" * 64)

    admin.sa.add_repo("release1", "build2", "path2", 2, "2" * 64)

    with raises.sync_error(sync_db.error.FILE_PATH_NOT_UNIQUE):
        admin.sa.add_repo("release1", "build3", "path1", 3, "3" * 64)

def test_complete_repo_uuid(admin):
    repo1 = admin.sa.add_repo("release1", "build1", "path1", 1, "1" * 64)
    repo2 = admin.sa.add_repo("release2", "build2", "path2", 2, "2" * 64)

    assert admin.sa.complete_repo_uuid("") == sorted([repo1, repo2])
    assert admin.sa.complete_repo_uuid(repo1) == [repo1]
    assert admin.sa.complete_repo_uuid("x") == []

def test_get_repo(admin):
    repo1 = admin.sa.add_repo("release1", "build1", "path1", 1, "1" * 64)
    repo2 = admin.sa.add_repo("release2", "build2", "path2", 2, "2" * 64)

    assert admin.sa.get_repo(repo1) == (repo1, "release1", "build1", "path1",
                                        1, "1" * 64)
    assert admin.sa.get_repo(repo2) == (repo2, "release2", "build2", "path2",
                                        2, "2" * 64)

    with raises.sync_error(sync_db.error.REPO_NOT_FOUND):
        admin.sa.get_repo("unknown")

    admin.sa.remove_repo(repo1)

    with raises.sync_error(sync_db.error.REPO_NOT_FOUND):
        admin.sa.get_repo(repo1)

def test_list_repos(admin):
    repo1 = admin.sa.add_repo("release1", "build1", "path1", 1, "1" * 64)
    repo2 = admin.sa.add_repo("release1", "build2", "path2", 2, "2" * 64)
    repo3 = admin.sa.add_repo("release2", "build2", "path3", 3, "3" * 64)

    repo1_row = (repo1, "release1", "build1", "path1")
    repo2_row = (repo2, "release1", "build2", "path2")
    repo3_row = (repo3, "release2", "build2", "path3")

    with raises.sync_error(sync_db.error.MULTIPLE_FILTERS):
        admin.sa.list_repos(release="release1", build="build1")

    assert admin.sa.list_repos() == sorted([repo1_row, repo2_row, repo3_row])

    assert admin.sa.list_repos(release="unknown") == []
    assert admin.sa.list_repos(build="unknown") == []
    assert admin.sa.list_repos(file_path="unknown") == []
    assert admin.sa.list_repos(file_hash="unknown") == []

    assert admin.sa.list_repos(release="release1") == sorted([repo1_row,
                                                           repo2_row])
    assert admin.sa.list_repos(build="build2") == sorted([repo2_row,
                                                          repo3_row])

    assert admin.sa.list_repos(file_path="path1") == [repo1_row]
    assert admin.sa.list_repos(file_hash="1" * 64) == [repo1_row]

    admin.sa.add_device("device", repo_uuid=repo1)

    assert admin.sa.list_repos(unused=True) == sorted([repo2_row, repo3_row])

def test_remove_repo(admin):
    repo1 = admin.sa.add_repo("release1", "build1", "path1", 1, "1" * 64)
    repo2 = admin.sa.add_repo("release2", "build2", "path2", 2, "2" * 64)

    with raises.sync_error(sync_db.error.REPO_NOT_FOUND):
        admin.sa.remove_repo("unknown")

    device = admin.sa.add_device("device", repo_uuid=repo1)

    with raises.sync_error(sync_db.error.REPO_IN_USE):
        admin.sa.remove_repo(repo1)

    admin.sa.remove_repo(repo2)

    admin.sa.remove_device(device)
    admin.sa.remove_repo(repo1)

    with raises.sync_error(sync_db.error.REPO_NOT_FOUND):
        admin.sa.remove_repo(repo1)
