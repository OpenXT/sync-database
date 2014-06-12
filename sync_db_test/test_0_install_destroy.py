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
import subprocess

import raises

def test_install(missing_db):
    db = missing_db

    db.run(["install"])
    db.get_owner_connection()

    with py.test.raises(subprocess.CalledProcessError):
        db.run(["install"])
    db.get_owner_connection()

    db.run(["run", "owner", "check-objects.sql"])
    db.run(["run", "admin", "check-objects.sql"])
    db.run(["run", "license", "check-objects.sql"])
    db.run(["run", "server", "check-objects.sql"])
    with py.test.raises(subprocess.CalledProcessError):
        db.run(["run", "owner", "does-not-exist.sql"])
    with py.test.raises(subprocess.CalledProcessError):
        db.run(["run", "invalid", "check-objects.sql"])

    target_version = db.get_target_version()
    assert db.run_version() == (target_version, target_version)

    db.run(["destroy", "--force"])
    with raises.db_error(raises.INVALID_USERNAME_OR_PASSWORD):
        db.get_owner_connection()
    with py.test.raises(subprocess.CalledProcessError):
        db.run_version()

    db.run(["destroy", "--force"])

def test_destroy(missing_db):
    db = missing_db

    db.run(["install"])
    db.get_owner_connection()

    with py.test.raises(subprocess.CalledProcessError):
        db.run(["destroy"], input_text="\n")
    db.get_owner_connection()

    db.run(["destroy"], input_text="yes\n")
    with raises.db_error(raises.INVALID_USERNAME_OR_PASSWORD):
        db.get_owner_connection()

def test_install_incomplete(missing_db):
    db = missing_db

    db.run(["install", "--to", "2"])

    target_version = db.get_target_version()
    assert db.run_version() == (target_version,
                                "incomplete installation of version "
                                "{0}".format(target_version))

    with py.test.raises(subprocess.CalledProcessError):
        db.run(["install"])
    with py.test.raises(subprocess.CalledProcessError):
        db.run(["upgrade"])
