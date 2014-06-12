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

import database

def pytest_addoption(parser):
    parser.addoption("--config",
                     action="store",
                     default=None,
                     help="sync-database configuration file")

def pytest_funcarg__db(request):
    def setup():
        return database.Database(request.config.option.config)

    def teardown(db):
        db.tear_down()

    return request.cached_setup(setup=setup,
                                teardown=teardown,
                                scope="session")

def pytest_funcarg__clean_db(request):
    db = request.getfuncargvalue("db")
    db.ensure_clean()
    return db

def pytest_funcarg__missing_db(request):
    db = request.getfuncargvalue("db")
    db.ensure_missing()
    return db

# Warning: If a test needs more than one of "admin", "license" and "server",
# use "clean_db" instead to avoid cleaning the database more than once. The
# admin, license and server connections can then be retrieved with
# get_admin_connection, get_license_connection and get_server_connection.

def pytest_funcarg__admin(request):
    db = request.getfuncargvalue("clean_db")
    return db.get_admin_connection()

def pytest_funcarg__license(request):
    db = request.getfuncargvalue("clean_db")
    return db.get_license_connection()

def pytest_funcarg__server(request):
    db = request.getfuncargvalue("clean_db")
    return db.get_server_connection()
