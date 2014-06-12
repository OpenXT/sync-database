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

import ConfigParser
import os
import re
import sys

DEFAULT_CONFIG_FILE = "~/.sync-database.conf"
USERS = ["owner", "admin", "license", "server"]
USER_PASSWORD_MESSAGE = ("must consist of one alphabetic character followed "
                         "by up to 29 alphanumeric or underscore characters")
CONFIG_SECTION = "database"
_CONFIG_FILE_ENV_VAR = "SYNC_DATABASE_CONF"

class Error(Exception):
    pass

def read_config(config_file):
    config_parser = ConfigParser.RawConfigParser()

    if config_file is None:
        config_file = os.path.expanduser(os.environ.get(_CONFIG_FILE_ENV_VAR,
                                                        DEFAULT_CONFIG_FILE))

    try:
        with open(config_file, "r") as f:
            config_parser.readfp(f)
    except IOError as error:
        raise Error("Error reading configuration file '{0}': {1}.\n\n"
                    "To generate the file interactively, run:\n\n"
                    "    {2} generate-config {3}".format(
                        config_file,
                        error.strerror,
                        get_script_name(),
                        config_file))

    config = {}

    for option in ["oracle_server", "sys_password"]:
        config[option] = config_parser.get(CONFIG_SECTION, option)

    for user in USERS:
        for suffix in ["user", "password"]:
            option = "sync_{0}_{1}".format(user, suffix)
            config[option] = config_parser.get(CONFIG_SECTION, option)

            if not check_user_or_password(option):
                raise Error("Error in configuration file: option '{0}' is not "
                            "valid: {1}.".format(option,
                                                 USER_PASSWORD_MESSAGE))

    return config

def check_user_or_password(value):
    return re.match(r"[a-zA-Z][a-zA-Z0-9_]{0,29}$", value) is not None

def write_config(config, config_file):
    with open(config_file, "w") as f:
        f.write("[{0}]\n".format(CONFIG_SECTION))

        for option in ["oracle_server", "sys_password"]:
            f.write("{0} = {1}\n".format(option, config[option]))

        for user in USERS:
            for suffix in ["user", "password"]:
                option = "sync_{0}_{1}".format(user, suffix)
                f.write("{0} = {1}\n".format(option, config[option]))

def get_script_name():
    return os.path.basename(sys.argv[0])
