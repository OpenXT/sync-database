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

import configuration

def add_subparser(subparsers):
    description = """Interactively generate a configuration file for
                     {0}.""".format(configuration.get_script_name())

    parser = subparsers.add_parser("generate-config",
                                   help="interactively generate configuration "
                                        "file",
                                   description=description)

    parser.add_argument("config_file",
                        metavar="CONFIG_FILE",
                        help="write configuration to this file")

    parser.set_defaults(func=_run)
    parser.set_defaults(need_config=False)
    parser.set_defaults(need_metadata=False)

def _run(args, metadata, config):
    new_config = {}

    new_config["oracle_server"] = _input_value(
        "Oracle server (blank for localhost)", None)

    new_config["sys_password"] = _input_value(
        "Password for user 'sys'", None)

    prefix = _input_user_or_password(
        "Unique prefix for user names", "sync")

    for user in configuration.USERS:
        user_name = "{0}_{1}".format(prefix, user)

        new_config["sync_{0}_user".format(user)] = user_name
        new_config["sync_{0}_password".format(user)] = _input_user_or_password(
            "Password for user '{0}'".format(user_name), user_name)

    configuration.write_config(new_config, args.config_file)

    print
    print "Configuration written to '{0}'.".format(args.config_file)

def _input_user_or_password(prompt, default):
    while True:
        response = _input_value(prompt, default)
        if configuration.check_user_or_password(response):
            return response
        print "Error: Value {0}.".format(configuration.USER_PASSWORD_MESSAGE)

def _input_value(prompt, default):
    if default is not None:
        default_text = " (default {0})".format(default)
    else:
        default_text = ""

    response = raw_input("{0}{1}: ".format(prompt, default_text))

    if response == "" and default is not None:
        return default
    else:
        return response
