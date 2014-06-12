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

import sqlplus

def add_subparser(subparsers):
    description = """Show the directory containing the sqlplus scripts for the
                     Synchronizer database."""

    parser = subparsers.add_parser("get-schema-dir",
                                   help="get schema directory",
                                   description=description)

    parser.set_defaults(func=_run)
    parser.set_defaults(need_config=False)
    parser.set_defaults(need_metadata=False)

def _run(args, metadata, config):
    if args.schema_dir:
        schema_dir = args.schema_dir
    else:
        schema_dir = sqlplus.get_default_schema_dir()

    print schema_dir
