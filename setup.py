#!/usr/bin/python
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

import os
from distutils.core import setup

# Generate bash completion script.
# TODO: This duplicates code from generate-completion script.
if os.path.isdir("sync_db_completion"):
    try:
        import sync_db
    except ImportError:
        # Useful when running from source tree.
        sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir,
                                     "sync-database"))
        import sync_db

    import sync_db.main
    import sync_db.configuration
    import sync_db_completion.main

    if not os.path.exists("generated"):
        os.mkdir("generated")

    parser = sync_db.main.create_parser()
    with open("generated/sync-database", "w") as cf:
        cf.write(sync_db_completion.main.format_script(
            parser,
            sync_db.configuration.USERS))

setup_cfg = {
    "name": "sync-database",
    "version": os.environ.get("VERSION"),
    "description": "XenClient Synchronizer XT database tool",
    "packages": ["sync_db"],
    "package_data": {"sync_db": ["schema/schema.json",
                                 "schema/*.sql",
                                 "schema/packages/*.sql"]},
    "scripts": ["sync-database"],
    "data_files":  [("/etc/bash_completion.d", ["generated/sync-database"])],
}

setup(**setup_cfg)
