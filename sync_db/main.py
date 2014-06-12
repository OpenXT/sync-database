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

import argparse
import ConfigParser
import sys

import configuration
import destroy
import generate_config
import get_schema_dir
import install
import run_script
import sqlplus
import version
import upgrade

# TODO: Exclude get-schema-dir command from help text, as it only exists for
#       the bash completion script.

def run():
    try:
        _run_command()
    except ConfigParser.Error as error:
        sys.stderr.write("Error in configuration file: {0}\n".format(error))
        sys.exit(1)
    except configuration.Error as error:
        sys.stderr.write("{0}\n".format(error))
        sys.exit(1)
    except (install.Error, sqlplus.Error, upgrade.Error,
            version.Error) as error:
        sys.stderr.write("Error: {0}\n".format(error))
        sys.exit(1)
    except KeyboardInterrupt:
        sys.stderr.write("Aborted.\n")
        sys.exit(1)

def _run_command():
    parser = create_parser()
    args = parser.parse_args()

    if args.need_metadata:
        metadata = sqlplus.get_metadata(args.schema_dir)
    else:
        metadata = None

    if args.need_config:
        config = configuration.read_config(args.config)
    else:
        config = None

    args.func(args, metadata, config)

def create_parser():
    epilog = """For more information about a command, run
                '{0} COMMAND -h'.""".format(configuration.get_script_name())

    parser = argparse.ArgumentParser(epilog=epilog)

    parser.add_argument("-c", "--config",
                        metavar="CONFIG_FILE",
                        help="configuration file (default {0})".format(
                            configuration.DEFAULT_CONFIG_FILE))

    # This argument only exists for benefit of the unit tests.
    parser.add_argument("--schema-dir",
                        metavar="SCHEMA_DIR",
                        help=argparse.SUPPRESS)

    subparsers = parser.add_subparsers(title="commands",
                                       metavar="COMMAND")

    for module in [destroy,
                   generate_config,
                   get_schema_dir,
                   install,
                   run_script,
                   upgrade,
                   version]:
        module.add_subparser(subparsers)

    return parser
