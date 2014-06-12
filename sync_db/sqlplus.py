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

import json
import os
import subprocess
import sys

_COMMANDS = """
connect {login}

set feedback off
set pagesize 0
set serveroutput on format wrapped
set verify off

whenever oserror exit failure
whenever sqlerror exit failure

define version = '{version}'

define sys_password = '{sys_password}'

define sync_owner_user = '{sync_owner_user}'
define sync_owner_password = '{sync_owner_password}'

define sync_admin_user = '{sync_admin_user}'
define sync_admin_password = '{sync_admin_password}'

define sync_license_user = '{sync_license_user}'
define sync_license_password = '{sync_license_password}'

define sync_server_user = '{sync_server_user}'
define sync_server_password = '{sync_server_password}'

@{script_path}
"""

class Error(Exception):
    pass

class ScriptError(Exception):
    pass

class ScriptWarning(Exception):
    pass

def get_metadata(schema_dir):
    if schema_dir is None:
        schema_dir = get_default_schema_dir()

    file_path = os.path.join(schema_dir, "schema.json")

    try:
        with open(file_path, "r") as f:
            try:
                return json.load(f)
            except ValueError as error:
                raise Error("Failed to read '{0}': {1}.".format(file_path,
                                                                error))
    except IOError as error:
        raise Error("Failed to read '{0}': {1}.".format(file_path,
                                                        error.strerror))

def run_steps(steps, metadata, config, schema_dir, list_steps, from_step,
              to_step, verbose, expect_output=False):
    if schema_dir is None:
        schema_dir = get_default_schema_dir()

    for step_num in from_step, to_step:
        if step_num is not None and (step_num < 1 or step_num > len(steps)):
            raise Error("Invalid step number {0}. Valid range is 1 to "
                        "{1}.".format(step_num, len(steps)))

    for i, (user, script) in enumerate(steps):
        step_num = i + 1

        if ((from_step is not None and step_num < from_step) or
            (to_step is not None and step_num > to_step)):
            continue

        if list_steps or verbose:
            print "Step {0}: {1} {2}".format(step_num, user, script)

        if not list_steps:
            output = []

            try:
                output.append(_run_script(user,
                                          script,
                                          metadata,
                                          config,
                                          schema_dir,
                                          expect_output))
            except ScriptError as error:
                raise Error("Failed at step {0}.\n\n"
                            "{1}".format(step_num, error))
            except ScriptWarning as error:
                sys.stderr.write("Warning at step {0}.\n\n"
                                 "{1}".format(step_num, error))

            if expect_output:
                return output

def _run_script(user, script, metadata, config, schema_dir, expect_output):
    if os.path.isabs(script):
        script_path = script
    else:
        script_path = os.path.join(schema_dir,
                                   os.path.join(*script.split("/")))

    try:
        with open(script_path) as f:
            pass
    except IOError as error:
        raise ScriptError("User: {0}\n"
                          "Script: {1}\n\n"
                          "Failed to read script '{2}': "
                          "{3}.".format(user,
                                        script,
                                        script_path,
                                        error.strerror))

    commands = _COMMANDS.format(login=_get_login(user, config),
                                script_path=script_path,
                                version=metadata["version"],
                                **config)

    try:
        process = subprocess.Popen(["sqlplus", "-l", "-s", "/nolog"],
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
    except OSError as error:
        raise Error("Failed to execute sqlplus: {0}.\n\n"
                    "Check that PATH includes "
                    "$ORACLE_HOME/bin.\n".format(error.strerror))

    output, _ = process.communicate(commands)

    if process.returncode != 0 or (output != "" and not expect_output):
        message = ("User: {0}\n"
                   "Script: {1}\n"
                   "Exit status: {2}\n\n"
                   "{3}".format(user, script, process.returncode, output))
        if process.returncode != 0:
            raise ScriptError(message)
        else:
            raise ScriptWarning(message)

    if expect_output:
        return output

def get_default_schema_dir():
    return os.path.join(os.path.dirname(__file__), "schema")

def _get_login(user, config):
    if user == "sys":
        login = "sys/{sys_password}"
        privilege = " as sysdba"
    else:
        login = "{sync_" + user + "_user}/{sync_" + user + "_password}"
        privilege = ""

    if config["oracle_server"]:
        service = "@" + config["oracle_server"]
    else:
        service = ""

    return (login + service + privilege).format(**config)
