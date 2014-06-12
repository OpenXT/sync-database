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

import cx_Oracle

import sync_db.error

class SyncLicense:
    def __init__(self, connection):
        self.connection = connection

    def deny_requested_license(self, device_uuid):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            cursor.callproc(
                "sync_license.deny_requested_license",
                keywordParameters={
                    "device_uuid": device_uuid})

    def expire_random_licenses(self):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            cursor.callproc(
                "sync_license.expire_random_licenses")

    def grant_requested_license(self, device_uuid, license_expiry_time,
                                license_hash):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            cursor.callproc(
                "sync_license.grant_requested_license",
                keywordParameters={
                    "device_uuid": device_uuid,
                    "license_expiry_time": license_expiry_time,
                    "license_hash": license_hash})

    def lock_next_expired_license(self, prev_device_uuid):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            device_uuid = cursor.callfunc(
                "sync_license.lock_next_expired_license",
                cx_Oracle.STRING,
                keywordParameters={
                    "prev_device_uuid": prev_device_uuid})
            return device_uuid

    def lock_next_requested_license(self, prev_device_uuid):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            device_uuid = cursor.callfunc(
                "sync_license.lock_next_requested_license",
                cx_Oracle.STRING,
                keywordParameters={
                    "prev_device_uuid": prev_device_uuid})
            return device_uuid

    def set_num_offline_licenses(self, num_offline_licenses):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            cursor.callproc(
                "sync_license.set_num_offline_licenses",
                keywordParameters={
                    "num_offline_licenses": num_offline_licenses})

    def revoke_all_licenses(self):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            cursor.callproc(
                "sync_license.revoke_all_licenses")

    def revoke_expired_license(self, device_uuid):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            cursor.callproc(
                "sync_license.revoke_expired_license",
                keywordParameters={
                    "device_uuid": device_uuid})

    def skip_expired_license(self):
        with sync_db.error.convert():
            cursor = self.connection.cursor()
            cursor.callproc(
                "sync_license.skip_expired_license")
