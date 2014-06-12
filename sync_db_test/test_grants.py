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

import cx_Oracle
import py.test

import raises

def test_admin_insert(clean_db):
    check_insert(clean_db, clean_db.get_admin_connection().connection)

def test_admin_update(clean_db):
    check_update(clean_db, clean_db.get_admin_connection().connection)

def test_admin_delete(clean_db):
    check_delete(clean_db, clean_db.get_admin_connection().connection)

def test_server_insert(clean_db):
    check_insert(clean_db, clean_db.get_server_connection().connection)

def test_server_update(clean_db):
    check_update(clean_db, clean_db.get_server_connection().connection)

def test_server_delete(clean_db):
    check_delete(clean_db, clean_db.get_server_connection().connection)

def check_insert(db, connection):
    for table in db.ALL_TABLES:
        cursor = connection.cursor()
        with raises.db_error(raises.INSUFFICIENT_PRIVILEGES):
            cursor.execute("insert into {0} "
                           "select * from {0} where 0 = 1".format(table))

def check_update(db, connection):
    for table in db.ALL_TABLES:
        select_cursor = connection.cursor()
        select_cursor.execute("select column_name "
                              "from all_tab_columns "
                              "where table_name = upper(:table_name) and "
                              "      column_id = 1",
                              table_name=table)
        column = select_cursor.fetchall()[0][0]

        update_cursor = connection.cursor()
        with raises.db_error(raises.INSUFFICIENT_PRIVILEGES):
            update_cursor.execute("update {0} "
                                  "set {1} = {1} "
                                  "where 0 = 1".format(table, column))

def check_delete(db, connection):
    for table in db.ALL_TABLES:
        cursor = connection.cursor()
        with raises.db_error(raises.INSUFFICIENT_PRIVILEGES):
            cursor.execute("delete from {0} "
                           "where 0 = 1".format(table))

def test_admin_execute(clean_db):
    admin = clean_db.get_admin_connection()
    cursor = admin.connection.cursor()
    with raises.db_error(raises.PLSQL_COMPILATION_ERROR):
        cursor.callfunc("sync_server.get_device_secret",
                        cx_Oracle.STRING,
                        keywordParameters={
                            "device_uuid": None})

def test_server_execute(clean_db):
    server = clean_db.get_server_connection()
    cursor = server.connection.cursor()
    with raises.db_error(raises.PLSQL_COMPILATION_ERROR):
        cursor.callfunc("sync_admin.add_device",
                        cx_Oracle.STRING,
                        keywordParameters={
                            "device_name": None,
                            "config": None})
