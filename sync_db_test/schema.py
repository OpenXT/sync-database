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

import cx_Oracle
import difflib

def dump_schema(db):
    schema = []

    for connection in [db.get_owner_connection().connection,
                       db.get_admin_connection().connection,
                       db.get_license_connection().connection,
                       db.get_server_connection().connection]:
        schema += _dump_user(connection) + [""]

    return schema

def _dump_user(connection):
    return (_dump_tables(connection) +
            _dump_table_columns(connection) +
            _dump_constraints(connection) +
            _dump_constraint_columns(connection) +
            _dump_indexes(connection) +
            _dump_index_columns(connection) +
            _dump_triggers(connection) +
            _dump_trigger_ordering(connection) +
            _dump_views(connection) +
            _dump_sequences(connection) +
            _dump_synonyms(connection) +
            _dump_source(connection) +
            _dump_objects(connection) +
            _dump_system_privileges(connection) +
            _dump_object_privileges(connection))

def _dump_tables(connection):
    return _select(connection,
                   "select user, "
                   "       'table' type_, "
                   "       table_name, "
                   "       status, "
                   "       temporary, "
                   "       duration "
                   "from user_tables")

def _dump_table_columns(connection):
    return _select(connection,
                   "select user, "
                   "       'table_column' type_, "
                   "       table_name, "
                   "       column_name, "
                   "       data_type, "
                   "       data_length, "
                   "       data_precision, "
                   "       data_scale, "
                   "       nullable "
                   "from user_tab_columns")

def _dump_constraints(connection):
    return _select(connection,
                   "select user, "
                   "       'constraint' type_, "
                   "       table_name, "
                   "       decode(generated, "
                   "              'GENERATED NAME', '(generated)', "
                   "              constraint_name) constraint_name, "
                   "       constraint_type, "
                   "       search_condition, "
                   "       r_owner, "
                   "       r_constraint_name, "
                   "       delete_rule, "
                   "       status, "
                   "       deferrable, "
                   "       deferred, "
                   "       rely, "
                   "       index_name "
                   "from user_constraints "
                   "where table_name not like 'BIN$%'",
                   respace=["search_condition"])

def _dump_constraint_columns(connection):
    return _select(connection,
                   "select user, "
                   "       'constraint_column' type_, "
                   "       table_name, "
                   "       decode(generated, "
                   "              'GENERATED NAME', '(generated)', "
                   "              constraint_name) constraint_name_, "
                   "       column_name "
                   "from user_constraints "
                   "     join user_cons_columns using (table_name, "
                   "                                   constraint_name) "
                   "where table_name not like 'BIN$%' "
                   "order by table_name, "
                   "         constraint_name_, "
                   "         column_name")

def _dump_indexes(connection):
    return _select(connection,
                   "select user, "
                   "       'index' type_, "
                   "       index_name, "
                   "       index_type, "
                   "       table_owner, "
                   "       table_name, "
                   "       table_type, "
                   "       uniqueness, "
                   "       compression, "
                   "       prefix_length, "
                   "       status, "
                   "       temporary, "
                   "       duration, "
                   "       visibility "
                   "from user_indexes")

def _dump_index_columns(connection):
    return _select(connection,
                   "select user, "
                   "       'index_column' type_, "
                   "       index_name, "
                   "       table_name, "
                   "       column_name, "
                   "       column_position, "
                   "       column_length, "
                   "       char_length, "
                   "       descend "
                   "from user_ind_columns "
                   "where table_name not like 'BIN$%'")

def _dump_triggers(connection):
    return _select(connection,
                   "select user, "
                   "       'trigger' type_, "
                   "       trigger_name, "
                   "       trigger_type, "
                   "       triggering_event, "
                   "       base_object_type, "
                   "       table_name, "
                   "       referencing_names, "
                   "       when_clause, "
                   "       status, "
                   "       action_type, "
                   "       trigger_body, "
                   "       before_statement, "
                   "       before_row, "
                   "       after_row, "
                   "       after_statement "
                   "from user_triggers",
                   respace=["when_clause", "trigger_body"])

def _dump_trigger_ordering(connection):
    return _select(connection,
                   "select user, "
                   "       'trigger_ordering' type_, "
                   "       trigger_name, "
                   "       referenced_trigger_owner, "
                   "       referenced_trigger_name, "
                   "       ordering_type "
                   "from user_trigger_ordering")

def _dump_views(connection):
    return _select(connection,
                   "select user, "
                   "       'view' type_, "
                   "       view_name, "
                   "       text, "
                   "       read_only "
                   "from user_views",
                   respace=["text"])

def _dump_sequences(connection):
    return _select(connection,
                   "select user, "
                   "       'sequence' type_, "
                   "       sequence_name, "
                   "       min_value, "
                   "       max_value, "
                   "       increment_by, "
                   "       cycle_flag, "
                   "       order_flag, "
                   "       cache_size "
                   "from user_sequences")

def _dump_synonyms(connection):
    return _select(connection,
                   "select user, "
                   "       'synonym' type_, "
                   "       synonym_name, "
                   "       table_owner, "
                   "       table_name "
                   "from user_synonyms")

def _dump_source(connection):
    return _select(connection,
                   "select user, "
                   "       'source' type_, "
                   "       name, "
                   "       type, "
                   "       line, "
                   "       text "
                   "from user_source "
                   "order by name, "
                   "         type, "
                   "         line",
                   sort=False)

def _dump_objects(connection):
    return _select(connection,
                   "select user, "
                   "       'object' type_, "
                   "       object_name, "
                   "       subobject_name, "
                   "       object_type, "
                   "       status, "
                   "       temporary, "
                   "       generated, "
                   "       namespace "
                   "from user_objects ")

def _dump_system_privileges(connection):
    return _select(connection,
                   "select user, "
                   "       'system privilege' type_, "
                   "       privilege, "
                   "       admin_option "
                   "from user_sys_privs")

def _dump_object_privileges(connection):
    return _select(connection,
                   "select user, "
                   "       'object privilege' type_, "
                   "       owner, "
                   "       table_name, "
                   "       grantor, "
                   "       privilege, "
                   "       grantable, "
                   "       hierarchy "
                   "from user_tab_privs "
                   "where table_name not like 'BIN$%'")

def _select(connection, query, sort=True, respace=[]):
    cursor = connection.cursor()
    cursor.execute(query)

    column_nums = {}
    for i, column_desc in enumerate(cursor.description):
        column_nums[column_desc[0].lower()] = i

    respace_nums = set(column_nums[column_name] for column_name in respace)

    lines = []
    for row in cursor:
        lines.append(" ".join(repr(_respace(x) if i in respace_nums else x)
                              for i, x in enumerate(row)))

    return sorted(lines) if sort else lines

def _respace(value):
    if value is not None:
        return " ".join(value.split())

def compare_schemas(schema1, schema2, schema_name1, schema_name2):
    matched = True

    for line in difflib.unified_diff(schema1,
                                     schema2,
                                     schema_name1,
                                     schema_name2,
                                     lineterm=""):
        print line
        matched = False

    assert matched
