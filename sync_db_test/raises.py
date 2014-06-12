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

import contextlib
import cx_Oracle
import py.test

import sync_db.error

# Oracle error codes.
INVALID_USERNAME_OR_PASSWORD = 1017
INSUFFICIENT_PRIVILEGES      = 1031
PLSQL_COMPILATION_ERROR      = 6550

# TODO: Improve output when assertion isn't raised or has wrong code.

@contextlib.contextmanager
def db_error(code=None):
    __tracebackhide__ = True

    with py.test.raises(cx_Oracle.DatabaseError) as error:
        yield

    if code is not None:
        assert error.value[0].code == code

@contextlib.contextmanager
def sync_error(code):
    __tracebackhide__ = True

    with py.test.raises(sync_db.error.SyncError) as error:
        yield

    assert error.value.code == code
