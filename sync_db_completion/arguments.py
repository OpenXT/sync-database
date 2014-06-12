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

# TODO: Reduce code duplication with sync-cli.

def get_commands(parser):
    assert len(parser._subparsers._group_actions) == 1

    action = parser._subparsers._group_actions[0]

    assert action.nargs == argparse.PARSER
    assert len(action.option_strings) == 0

    return sorted(action.choices.keys())

def get_command_args(parser, command):
    if command is not None:
        parser = parser._subparsers._group_actions[0].choices[command]

    args = []

    for action in parser._actions:
        assert ((action.metavar is None and
                 action.nargs == 0) or
                (action.metavar is not None and
                 (action.nargs is None or
                  action.nargs == argparse.PARSER)))
        args.append((action.option_strings, action.metavar))

    hints = parser._defaults.get("completion_hints", {})

    return args, hints
