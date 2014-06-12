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
import os
import re

AUTH_TOKEN_REQUIRED         = 20000
AUTH_TOKEN_TOO_LONG         = 20001
DEVICE_NAME_REQUIRED        = 20002
DEVICE_NAME_TOO_LONG        = 20003
DEVICE_NOT_FOUND            = 20004
DEVICE_REQUIRED             = 20005
DISK_NAME_REQUIRED          = 20006
DISK_NAME_TOO_LONG          = 20007
DISK_NOT_FOUND              = 20008
DISK_REPEATED               = 20009
DISK_REQUIRED               = 20010
ENCRYPTION_KEY_INVALID      = 20011
FILE_HASH_INVALID           = 20013
FILE_HASH_REQUIRED          = 20014
FILE_PATH_NOT_UNIQUE        = 20015
FILE_PATH_REQUIRED          = 20016
FILE_PATH_TOO_LONG          = 20017
FILE_SIZE_INVALID           = 20018
FILE_SIZE_REQUIRED          = 20019
MULTIPLE_FILTERS            = 20020
VM_INST_EXISTS              = 20029
VM_INST_NAME_REQUIRED       = 20030
VM_INST_NAME_TOO_LONG       = 20031
VM_INST_NOT_FOUND           = 20032
VM_INST_REQUIRED            = 20033
VM_NAME_REQUIRED            = 20034
VM_NAME_TOO_LONG            = 20035
VM_NOT_FOUND                = 20036
VM_REQUIRED                 = 20037
CONFIG_EMPTY                = 20038
CONFIG_INVALID              = 20039
CONFIG_DAEMON_TOO_LONG      = 20040
CONFIG_KEY_TOO_LONG         = 20041
CONFIG_VALUE_TOO_LONG       = 20042
VM_IN_USE                   = 20043
DISK_IN_USE                 = 20044
DEVICE_HAS_VM_INST          = 20047
VM_INST_ALREADY_LOCKED      = 20048
VM_INST_ALREADY_UNLOCKED    = 20049
VM_INST_ALREADY_REMOVED     = 20056
VM_INST_NOT_REMOVED         = 20057
VM_INST_REMOVED             = 20058
REMOVED_VM_INST_EXISTS      = 20060
BUILD_REQUIRED              = 20061
BUILD_TOO_LONG              = 20062
RELEASE_REQUIRED            = 20063
RELEASE_TOO_LONG            = 20064
REPO_EXISTS                 = 20065
REPO_IN_USE                 = 20071
REPO_NOT_FOUND              = 20072
REPO_REQUIRED               = 20073
EXPIRED_LICENSE_NOT_FOUND   = 20074
REQUESTED_LICENSE_NOT_FOUND = 20075
INSTALLATION_INCOMPLETE     = 20076
UPGRADE_INCOMPLETE          = 20077
DB_STATE_INVALID            = 20078
DB_VERSION_INCOMPATIBLE     = 20079
DISK_TYPE_INVALID           = 20080
ISO_WITH_ENCRYPTION_KEY     = 20081
ISO_NOT_READ_ONLY           = 20082
DISK_READ_ONLY_AND_SHARED   = 20083
TOO_MANY_CONFIG_ITEMS       = 20085
NUM_LICENSES_INVALID        = 20086
OFFLINE_LICENSING           = 20087
OUT_OF_LICENSES             = 20088

_MESSAGES = {
    AUTH_TOKEN_REQUIRED:         "Authentication token must be specified.",
    AUTH_TOKEN_TOO_LONG:         "Authentication token '{0}' is too long.",
    DEVICE_NAME_REQUIRED:        "Device name must be specified.",
    DEVICE_NAME_TOO_LONG:        "Device name '{0}' is too long.",
    DEVICE_NOT_FOUND:            "Device uuid '{0}' not found.",
    DEVICE_REQUIRED:             "Device uuid must be specified.",
    DISK_NAME_REQUIRED:          "Disk name must be specified.",
    DISK_NAME_TOO_LONG:          "Disk name '{0}' is too long.",
    DISK_NOT_FOUND:              "Disk uuid '{0}' not found.",
    DISK_REPEATED:               "Disk uuid '{0}' specified more than once.",
    DISK_REQUIRED:               "Disk uuid must be specified.",
    ENCRYPTION_KEY_INVALID:      "Encryption key is not valid.",
    FILE_HASH_INVALID:           "File hash '{0}' is not valid.",
    FILE_HASH_REQUIRED:          "File hash must be specified.",
    FILE_PATH_NOT_UNIQUE:        "File path '{0}' has already been added.",
    FILE_PATH_REQUIRED:          "File path must be specified.",
    FILE_PATH_TOO_LONG:          "File path '{0}' is too long.",
    FILE_SIZE_INVALID:           "File size {0} is not valid.",
    FILE_SIZE_REQUIRED:          "File size must be specified.",
    MULTIPLE_FILTERS:            "More than one filter specified.",
    VM_INST_EXISTS:              "VM instance uuid '{0}', an instance of VM "
                                 "uuid '{2}' on device uuid '{1}', already "
                                 "exists.",
    VM_INST_NAME_REQUIRED:       "VM instance name must be specified.",
    VM_INST_NAME_TOO_LONG:       "VM instance name '{0}' is too long.",
    VM_INST_NOT_FOUND:           "VM instance uuid '{0}' not found.",
    VM_INST_REQUIRED:            "VM instance must be specified.",
    VM_NAME_REQUIRED:            "VM name must be specified.",
    VM_NAME_TOO_LONG:            "VM name '{0}' is too long.",
    VM_NOT_FOUND:                "VM uuid '{0}' not found.",
    VM_REQUIRED:                 "VM uuid must be specified.",
    CONFIG_EMPTY:                "Configuration item must not be empty.",
    CONFIG_INVALID:              "Configuration item '{0}' is not valid.",
    CONFIG_DAEMON_TOO_LONG:      "Configuration daemon '{0}' is too long.",
    CONFIG_KEY_TOO_LONG:         "Configuration key '{0}' is too long.",
    CONFIG_VALUE_TOO_LONG:       "Configuration value '{0}' is too long.",
    VM_IN_USE:                   "VM uuid '{0}' is used by one or more VM "
                                 "instances. This may include VM instances "
                                 "which have been removed. Use "
                                 "'purge-vm-instance' to permanently remove "
                                 "all information related to a VM instance.",
    DISK_IN_USE:                 "Disk uuid '{0}' is used by one or more VMs.",
    DEVICE_HAS_VM_INST:          "Device uuid '{0}' has one or more VM "
                                 "instances. See 'cascade' option.",
    VM_INST_ALREADY_LOCKED:      "VM instance uuid '{0}' is already locked.",
    VM_INST_ALREADY_UNLOCKED:    "VM instance uuid '{0}' is already unlocked.",
    VM_INST_ALREADY_REMOVED:     "VM instance uuid '{0}' has already been "
                                 "removed.",
    VM_INST_NOT_REMOVED:         "VM instance uuid '{0}' has not been "
                                 "removed.",
    VM_INST_REMOVED:             "VM instance uuid '{0}' has been removed.",
    REMOVED_VM_INST_EXISTS:      "VM instance uuid '{0}', an instance of VM "
                                 "uuid '{2}' on device uuid '{1}', has "
                                 "previously been removed. Use "
                                 "'readd-vm-instance' to re-add the VM "
                                 "instance.",
    BUILD_REQUIRED:              "Build must be specified.",
    BUILD_TOO_LONG:              "Build '{0}' is too long.",
    RELEASE_REQUIRED:            "Release identifier must be specified.",
    RELEASE_TOO_LONG:            "Release '{0}' is too long.",
    REPO_EXISTS:                 "Repository for release '{0}' and build "
                                 "'{1}' has already been added.",
    REPO_IN_USE:                 "Repository uuid '{0}' is in use by one or "
                                 "more devices.",
    REPO_NOT_FOUND:              "Repository uuid '{0}' not found.",
    REPO_REQUIRED:               "Repository must be specified.",
    EXPIRED_LICENSE_NOT_FOUND:   "Expired license for device uuid '{0}' not "
                                 "found.",
    REQUESTED_LICENSE_NOT_FOUND: "Requested license for device uuid '{0}' not "
                                 "found.",
    INSTALLATION_INCOMPLETE:     "Synchronizer database installation is "
                                 "incomplete. (Run 'sync-database version' "
                                 "for more information.)",
    UPGRADE_INCOMPLETE:          "Synchronizer database upgrade is "
                                 "incomplete. (Run 'sync-database version' "
                                 "for more information.)",
    DB_STATE_INVALID:            "Synchronizer database is not in a valid "
                                 "state. (Run 'sync-database version' for "
                                 "more information.)",
    DB_VERSION_INCOMPATIBLE:     "Synchronizer database version "
                                 "incompatibility. Database version is {0}. "
                                 "Version {1} is required.",
    DISK_TYPE_INVALID:           "Disk type '{0}' is not valid.",
    ISO_WITH_ENCRYPTION_KEY:     "Disk of type 'iso' cannot have encryption "
                                 "key.",
    ISO_NOT_READ_ONLY:           "Disk of type 'iso' must be read-only.",
    DISK_READ_ONLY_AND_SHARED:   "Read-only disk cannot be shared.",
    TOO_MANY_CONFIG_ITEMS:       "No more than {0} configuration items can be "
                                 "specified.",
    NUM_LICENSES_INVALID:        "Number of licenses {0} is not valid.",
    OFFLINE_LICENSING:           "Licensing mode is set to offline.",
    OUT_OF_LICENSES:             "All offline licenses are in use.",
}

class Error(Exception):
    def __init__(self, error):
        self.code = error[0].code
        self._message = error[0].message

    def __str__(self):
        return self._message.rstrip(os.linesep)

class SyncError(Error):
    def __init__(self, error):
        self.code = error[0].code
        self._message = error[0].message

        match = re.match(r"ORA-\d+: sync((?:\|[^\n]*)?)", self._message)

        if match is not None:
            self._params = match.group(1).split("|")[1:]
        else:
            self._params = None

    def __str__(self):
        try:
            return _MESSAGES[self.code].format(*self._params)
        except (AttributeError, IndexError, KeyError):
            return self._message.rstrip(os.linesep)

    @classmethod
    def can_convert(cls, error):
        return error[0].code in _MESSAGES

@contextlib.contextmanager
def convert():
    try:
        yield
    except cx_Oracle.Error as error:
        if SyncError.can_convert(error):
            raise SyncError(error)
        else:
            raise Error(error)
