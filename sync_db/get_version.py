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

class Error(Exception):
    pass

def get_version(metadata, config, schema_dir):
    output = sqlplus.run_steps([["owner", "get-version.sql"]],
                                metadata,
                                config,
                                schema_dir,
                                False,
                                None,
                                None,
                                False,
                                expect_output=True)

    data = {}

    for line in output[0].splitlines():
        fields = line.split(":", 1)

        if len(fields) < 2:
            raise Error("Failed to determine database version.\n\n"
                        "{0}".format(output[0]))

        data[fields[0]] = fields[1] or None

    try:
        return data["current_version"], data["installing_version"]
    except KeyError:
        raise Error("Failed to determine database version.\n\n"
                    "{0}".format(output[0]))
