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

import sync_admin
import sync_license
import sync_server
import sync_version

class AdminConnection:
    def __init__(self, user, password, server=""):
        self.connection = cx_Oracle.connect(user, password, server)

        self.sa = sync_admin.SyncAdmin(self.connection)
        self.sv = sync_version.SyncVersion(self.connection)

class LicenseConnection:
    def __init__(self, user, password, server=""):
        self.connection = cx_Oracle.connect(user, password, server)

        self.sl = sync_license.SyncLicense(self.connection)
        self.sv = sync_version.SyncVersion(self.connection)

class OwnerConnection:
    def __init__(self, user, password, server=""):
        self.connection = cx_Oracle.connect(user, password, server)

class ServerConnection:
    def __init__(self, user, password, server=""):
        self.connection = cx_Oracle.connect(user, password, server)

        self.ss = sync_server.SyncServer(self.connection)
        self.sv = sync_version.SyncVersion(self.connection)
