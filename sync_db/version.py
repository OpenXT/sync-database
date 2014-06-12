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

import arguments
import sqlplus
import get_version

class Error(Exception):
    pass

def add_subparser(subparsers):
    description = """Show the schema version currently installed in the
                     Synchronizer database. Report whether this matches the
                     target schema version, i.e. the version that would be
                     installed by the 'install' or 'upgrade' command."""

    parser = subparsers.add_parser("version",
                                   help="show database schema version",
                                   description=description)

    parser.set_defaults(func=_run)
    parser.set_defaults(need_config=True)
    parser.set_defaults(need_metadata=True)

def _run(args, metadata, config):
    target_version = metadata["version"]
    can_upgrade_from = metadata["upgrade-from"]

    print "Target schema version: {0}".format(target_version)

    try:
        (current_version,
         installing_version) = get_version.get_version(metadata,
                                                       config,
                                                       args.schema_dir)
    except get_version.Error as error:
        raise Error("Database schema version unknown.\n\n{0}".format(error))

    if installing_version is None:
        if current_version is None:
            raise Error("Database schema version unknown.")

        print ("Database schema version: {0}".format(current_version))

        if current_version == target_version:
            print "\nDatabase schema is up-to-date."
        elif current_version in can_upgrade_from:
            print ("\nTo upgrade database to schema version {0}, use the "
                   "'upgrade' command.".format(target_version))
        else:
            print ("\nDirect upgrade from schema version {0} to {1} is not "
                   "supported.".format(current_version, target_version))

            if can_upgrade_from:
               print ("Supported schema versions for upgrade: "
                      "{0}".format(", ".join(can_upgrade_from)))
    else:
        if current_version is None:
            print ("Database schema version: incomplete installation of "
                   "version {0}".format(installing_version))
            if installing_version == target_version:
                print ("\nConsider destroying the database (this will destroy "
                       "all data) and using the 'install' command to "
                       "reattempt installation of schema version "
                       "{0}.".format(target_version))
        else:
            print ("Database schema version: incomplete upgrade from version "
                   "{0} to {1}".format(current_version, installing_version))
            if installing_version == target_version:
                print ("\nTo reattempt upgrade to schema version {0}, use the "
                       "'upgrade' command with the '--retry' "
                       "option.".format(target_version))
