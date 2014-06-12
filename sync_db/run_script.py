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

import os

import configuration
import sqlplus

def add_subparser(subparsers):
    description = """Run a single sqlplus script."""

    epilog = """SCRIPT is assumed to be relative to schema directory (default
                {0}) unless it begins with '{1}'.""".format(
                 sqlplus.get_default_schema_dir(), os.path.sep)

    parser = subparsers.add_parser("run",
                                   help="run a single sqlplus script",
                                   description=description,
                                   epilog=epilog)

    parser.add_argument("user",
                        metavar="USER",
                        choices=["sys"] + configuration.USERS,
                        help="connect to database as: " +
                             ", ".join(["sys"] + configuration.USERS))

    parser.add_argument("script",
                        metavar="SCRIPT",
                        help="sqlplus script to run")

    parser.set_defaults(func=_run)
    parser.set_defaults(need_config=True)
    parser.set_defaults(need_metadata=True)

def _run(args, metadata, config):
    sqlplus.run_steps([(args.user, args.script)],
                      metadata,
                      config,
                      args.schema_dir,
                      False,
                      None,
                      None,
                      False)
