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
    description = """Upgrades the Synchronizer database."""

    parser = subparsers.add_parser("upgrade",
                                   help="upgrade database",
                                   description=description)

    arguments.add_step_args(parser)

    parser.add_argument("--retry",
                        action="store_true",
                        help="retry failed upgrade")

    parser.add_argument("--force",
                        action="store_true",
                        help="allow upgrade even if schema is up-to-date")

    parser.set_defaults(func=_run)
    parser.set_defaults(need_config=True)
    parser.set_defaults(need_metadata=True)

def _run(args, metadata, config):
    _check_schema_version(args, metadata, config)

    sqlplus.run_steps(metadata["commands"]["upgrade"],
                      metadata,
                      config,
                      args.schema_dir,
                      args.list_steps,
                      args.from_step,
                      args.to_step,
                      args.verbose)

def _check_schema_version(args, metadata, config):
    target_version = metadata["version"]
    can_upgrade_from = metadata["upgrade-from"]

    try:
        (current_version,
         installing_version) = get_version.get_version(metadata,
                                                       config,
                                                       args.schema_dir)
    except get_version.Error:
        raise Error("Database not installed.")

    if current_version is None:
        if installing_version is None:
            raise Error("Database schema version unknown.")
        else:
            raise Error("Incomplete database installation exists. Run "
                        "'version' command for more information.")

    if installing_version is not None:
        if installing_version != target_version:
            raise Error("Previous upgrade is incomplete. Run 'version' "
                        "command for more information.")

        if not args.retry:
            raise Error("Previous upgrade is incomplete. Use '--retry' "
                        "option to reattempt upgrade. Run 'version' command "
                        "for more information.")

    if current_version == target_version:
        if not args.force:
            raise Error("Database is already up-to-date. Run 'version' "
                        "command for more information.")
    elif current_version not in can_upgrade_from:
        raise Error("Direct upgrade from schema version {0} to {1} is not "
                    "supported. Run 'version' command for more "
                    "information.".format(current_version, target_version))
