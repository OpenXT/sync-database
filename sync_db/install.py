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
import get_version
import sqlplus

class Error(Exception):
    pass

def add_subparser(subparsers):
    description = """Install the Synchronizer database."""

    parser = subparsers.add_parser("install",
                                   help="install database",
                                   description=description)

    arguments.add_step_args(parser)

    parser.set_defaults(func=_run)
    parser.set_defaults(need_config=True)
    parser.set_defaults(need_metadata=True)

def _run(args, metadata, config):
    _check_schema_version(args, metadata, config)

    sqlplus.run_steps(metadata["commands"]["install"],
                      metadata,
                      config,
                      args.schema_dir,
                      args.list_steps,
                      args.from_step,
                      args.to_step,
                      args.verbose)

def _check_schema_version(args, metadata, config):
    try:
        (current_version,
         installing_version) = get_version.get_version(metadata,
                                                       config,
                                                       args.schema_dir)

        if current_version or installing_version:
            raise Error("Database already installed.")
    except get_version.Error:
        pass
