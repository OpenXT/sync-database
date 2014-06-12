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

import arguments
import templates

# TODO: Reduce code duplication with sync-cli.

_FUNC    = 0
_COMMAND = 1

completions = {
    "COMMAND":     (_FUNC, "_sync_database_complete_command"),
    "CONFIG_FILE": (_FUNC, "_sync_database_complete_file_path"),
    "SCHEMA_DIR":  (_FUNC, "_sync_database_complete_dir_path"),
    "SCRIPT":      (_FUNC, "_sync_database_complete_script"),
    "STEP_NUM":    None,
    "USER":        (_FUNC, "_sync_database_complete_user"),
}

def format_script(parser, users):
    commands = arguments.get_commands(parser)
    commands = arguments.get_commands(parser)

    return _format(templates.SCRIPT,
                   {"COMMAND_CASES": _format_command_cases(commands),
                    "COMMAND_LIST": _format_command_list(commands),
                    "COMMAND_FUNCS": _format_command_funcs(parser, commands),
                    "USER_LIST": _format_user_list(users)})

def _format_command_cases(commands):
    command_cases = []

    for command in commands:
        command_cases.append(_format(templates.COMMAND_CASE,
                                     {"COMMAND": command,
                                      "SANITISED_COMMAND": _sanitise(command)}))

    return "\n".join(command_cases)

def _format_command_list(commands):
    return " ".join(commands)

def _format_command_funcs(parser, commands):
    funcs = [_format_funcs_for_command(parser,
                                       None,
                                       "initial",
                                       "_sync_database_complete_initial_arg")]

    for command in commands:
        funcs.append(_format_funcs_for_command(
            parser,
            command,
            _sanitise(command),
            "_sync_database_complete_command_arg"))

    return "\n".join(funcs)

def _format_user_list(users):
    return " ".join(users)

def _format_funcs_for_command(parser, command, sanitised_command, next_func):
    short_no_val_opts = []
    short_one_val_opts = []
    long_one_val_opts = []
    all_opts = []
    opt_metavars = {}
    pos_metavars = []

    args, hints = arguments.get_command_args(parser, command)

    for opts, metavar in args:
        if len(opts) > 0:
            patterns = []
            for opt in opts:
                all_opts.append(opt)
                if opt.startswith("--"):
                    if metavar is not None:
                        u = _get_unambiguous_prefix(opt, args)
                        if u != opt:
                            patterns.append(u + "*")
                        else:
                            patterns.append(opt)
                        for i in range(len(u), len(opt) + 1):
                            long_one_val_opts.append(opt[:i])
                else:
                    if metavar is not None:
                        short_one_val_opts.append(opt)
                        patterns.append(opt)
                    else:
                        short_no_val_opts.append(opt)
            if metavar is not None:
                opt_metavars["|".join(patterns)] = metavar
        else:
            pos_metavars.append(metavar)

    return _format(templates.COMMAND_FUNCS,
                   {"SANITISED_COMMAND": sanitised_command,
                    "SHORT_NO_VAL": _combine_short_opts(short_no_val_opts),
                    "SHORT_ONE_VAL": _combine_short_opts(short_one_val_opts),
                    "LONG_ONE_VAL": _combine_long_opts(long_one_val_opts),
                    "NEXT_FUNC": next_func,
                    "ALL": " ".join(sorted(all_opts)),
                    "OPT_VALUE_CASES": _format_opt_value_cases(opt_metavars,
                                                               hints),
                    "POS_VALUE_CASES": _format_pos_value_cases(pos_metavars,
                                                               hints)})

def _get_unambiguous_prefix(opt, args):
    length = len("--") + 1
    for other_opts, _ in args:
        for other in other_opts:
            if other != opt:
                while other[:length] == opt[:length]:
                    length += 1
    return opt[:length]

def _combine_short_opts(opts):
    return "".join(opt[1:] for opt in sorted(opts))

def _combine_long_opts(opts):
    return "|".join(opt[2:] for opt in sorted(opts))

def _format_opt_value_cases(opt_metavars, hints):
    cases = []
    for pattern in sorted(opt_metavars.keys()):
        metavar = opt_metavars[pattern]
        cases.append(_format_value_case(pattern, metavar, hints))

    if len(cases) > 0:
        return _format(templates.OPT_VALUE_CASES,
                       {"VALUE_CASES": "\n".join(cases)})
    else:
        return ""

def _format_pos_value_cases(pos_metavars, hints):
    cases = []
    for i, metavar in enumerate(pos_metavars):
        cases.append(_format_value_case(i, metavar, hints))

    if len(cases) > 0:
        return _format(templates.POS_VALUE_CASES,
                       {"VALUE_CASES": "\n".join(cases)})
    else:
        return ""

def _format_value_case(pattern, metavar, hints):
    completion = _get_completion(metavar, hints)

    return _format(templates.VALUE_CASE,
                   {"PATTERN": pattern,
                    "COMPLETION": completion})

def _get_completion(metavar, hints):
    completion = completions[metavar]
    hint = " " + hints[metavar] if metavar in hints else ""

    if completion is None:
        return "return"
    elif completion[0] == _FUNC:
        return completion[1] + hint
    elif completion[0] == _COMMAND:
        return "_sync_database_run_command " + completion[1] + hint

def _sanitise(command):
    return command.replace("-", "_")

def _format(template, keywords):
    text = template
    for keyword, replacement in keywords.iteritems():
        text = text.replace("%" + keyword + "%", str(replacement))
    return text
