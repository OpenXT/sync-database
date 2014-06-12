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

import sync_db.error

class SyncVersion:
    def __init__(self, connection):
        self.connection = connection

    def check_version(self, required_version):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            cursor.callproc(
                "sync_version.check_version",
                keywordParameters={
                    "required_version": required_version})

    def get_version(self):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            current_version = cursor.callfunc(
                "sync_version.get_version",
                cx_Oracle.STRING)
            return current_version
