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

# TODO: Reduce code duplication with sync-cli.

SCRIPT = """\
# Bash completion for sync-database command.

# TODO: "--" should terminate options

_sync_database()
{
    local sync_database=$1
    local cur=$2

    local cmd
    local cmd_index
    local schema_dir

    COMPREPLY=()

    _sync_database_command_initial

    case $cmd in
%COMMAND_CASES%
    esac
}

_sync_database_complete_initial_arg()
{
    local opt
    local pos
    local prefix

    _sync_database_parse_args find_cmd 1 _sync_database_save

    if [[ -z $cmd ]] ; then
        if _sync_database_cur_is_opt ; then
            _sync_database_complete_opt
        else
            _sync_database_complete_value
        fi
    fi
}

_sync_database_save()
{
    local opt=$1
    local value=$2

    if [[ $opt == "-s" || $opt =~ ^--s ]] ; then
        schema_dir=$value
    fi
}

_sync_database_complete_command_arg()
{
    local opt
    local pos
    local prefix

    if _sync_database_cur_is_opt ; then
        _sync_database_complete_opt
    else
        _sync_database_parse_args all $((cmd_index + 1)) ""
        _sync_database_complete_value
    fi
}

_sync_database_cur_is_opt()
{
    [[ $cur =~ ^- ]]
}

_sync_database_complete_opt()
{
    if [[ $cur =~ ^-[$short_no_val]*[$short_no_val$short_one_val]$ ]] ; then
        _sync_database_accept
    elif [[ $cur =~ ^(-[$short_no_val]*)([$short_one_val])(.+)$ ]] ; then
        prefix="${BASH_REMATCH[1]}${BASH_REMATCH[2]}"
        cur=${BASH_REMATCH[3]}

        $complete_func opt_value "-${BASH_REMATCH[2]}"
    else
        $complete_func opt
    fi
}

_sync_database_complete_value()
{
    if [[ -n $opt ]] ; then
        $complete_func opt_value "$opt"
    else
        $complete_func pos_value "$pos"
    fi
}

_sync_database_parse_args()
{
    local mode=$1
    local start=$2
    local save_func=$3

    local i

    opt=
    pos=0

    if [[ $mode == find_cmd ]] ; then
        cmd=
        cmd_index=
    fi

    for ((i = start; i < COMP_CWORD; i++)) ; do
        local word=${COMP_WORDS[i]}

        if [[ $word =~ ^-[$short_no_val]*([$short_one_val])$ ]] ; then
            opt="-${BASH_REMATCH[1]}"
        elif [[ $word =~ ^--($long_one_val)$ ]] ; then
            opt="--${BASH_REMATCH[1]}"
        elif [[ $word =~ ^-[$short_no_val]*([$short_one_val])(.+)$ ]] ; then
            if [[ -n $save_func ]] ; then
                $save_func "-${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}"
            fi
            opt=
        elif [[ $word =~ ^- ]] ; then
            opt=
        elif [[ $word == "=" ]] ; then
            :
        elif [[ -n $opt ]] ; then
            if [[ -n $save_func ]] ; then
                $save_func "$opt" "$word"
            fi
            opt=
        elif [[ $mode == find_cmd ]] ; then
            cmd=$word
            cmd_index=$i
            break
        else
            ((pos++))
        fi
    done
}

#------------------------------------------------------------------------------

_sync_database_complete_command()
{
    local commands="%COMMAND_LIST%"

    case "$cur" in
        complete*)
            _sync_database_filter "$commands"
            ;;
        *)
            _sync_database_filter_exclude "$commands" "complete*"
            ;;
    esac
}

_sync_database_complete_script()
{
    case "$cur" in
        /*)
            _sync_database_complete_file_path
            ;;
        *)
            if [[ -z $schema_dir ]] ; then
                schema_dir=$("$sync_database" "get-schema-dir")
            fi

            local all_scripts=$(cd "$schema_dir" && shopt -o nullglob &&
                                echo *.sql */*.sql)

            COMPREPLY=($(compgen -P "$prefix" -W "$all_scripts" -- "$cur"))
            ;;
    esac
}

_sync_database_complete_user()
{
    local users="%USER_LIST%"

    _sync_database_filter "$users"
}

_sync_database_complete_file_path()
{
    compopt -o filenames
    COMPREPLY=($(compgen -P "$prefix" -f -- "$cur"))
}

_sync_database_complete_dir_path()
{
    compopt -o dirnames
    COMPREPLY=($(compgen -P "$prefix" -d -- "$cur"))
}

_sync_database_accept()
{
    COMPREPLY=($(compgen -P "$prefix" -W "$cur"))
}

_sync_database_filter()
{
    local completions=$1

    COMPREPLY=($(compgen -P "$prefix" -W "$completions" -- "$cur"))
}

_sync_database_filter_exclude()
{
    local completions=$1
    local exclude=$2

    COMPREPLY=($(compgen -P "$prefix" -W "$completions" -X "$exclude" -- "$cur"))
}

#------------------------------------------------------------------------------

%COMMAND_FUNCS%
#------------------------------------------------------------------------------

complete -F _sync_database sync-database
complete -F _sync_database ./sync-database
"""

COMMAND_CASE = """\
        %COMMAND%) _sync_database_command_%SANITISED_COMMAND% ;;"""
            
COMMAND_FUNCS = """\
_sync_database_command_%SANITISED_COMMAND%()
{
    local short_no_val="%SHORT_NO_VAL%"
    local short_one_val="%SHORT_ONE_VAL%"
    local long_one_val="%LONG_ONE_VAL%"
    local complete_func="_sync_database_helper_%SANITISED_COMMAND%"
    
    %NEXT_FUNC%
}   
    
_sync_database_helper_%SANITISED_COMMAND%()
{   
    case $1 in
        opt)
            _sync_database_filter "%ALL%"
            ;;
%OPT_VALUE_CASES%%POS_VALUE_CASES%    esac
}
"""

OPT_VALUE_CASES = """\

        opt_value)
            case $2 in
%VALUE_CASES%
            esac
            ;;  
"""

POS_VALUE_CASES = """\

        pos_value)
            case $2 in
%VALUE_CASES%
            esac
            ;;
"""

VALUE_CASE = """\
                %PATTERN%) %COMPLETION% ;;"""
