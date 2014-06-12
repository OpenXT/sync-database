/*
 * Copyright (c) 2013 Citrix Systems, Inc.
 * 
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

-- For each foreign key constraint, check that the columns are on the leading
-- edge of an index on the child table.

variable exit_status number;

declare
    cursor unindexed_foreign_keys is
        select lower(constraint_name) constraint_name
        from (select table_name,
                     constraint_name,
                     count(*) num_cols
              from user_constraints
                   join user_cons_columns using (owner,
                                                 table_name,
                                                 constraint_name)
              where constraint_type = 'R'
              group by table_name,
                       constraint_name) c
        where not exists (select null
                          from user_cons_columns
                               join user_ind_columns uic using (table_name,
                                                                column_name)
                          where table_name = c.table_name and
                                constraint_name = c.constraint_name and
                                uic.column_position <= c.num_cols
                          group by index_name
                          having count(*) = c.num_cols)
        order by constraint_name;

    found_unindexed_foreign_keys boolean := false;
begin
    for foreign_key in unindexed_foreign_keys
    loop
        found_unindexed_foreign_keys := true;

        dbms_output.put_line('Error: unindexed foreign key: ' ||
                             foreign_key.constraint_name);
    end loop;

    if found_unindexed_foreign_keys then
        :exit_status := 1;
    else
        :exit_status := 0;
    end if;
end;
/

exit :exit_status;
