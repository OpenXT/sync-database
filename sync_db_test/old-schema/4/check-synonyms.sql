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
    cursor broken_synonyms is
        select lower(synonym_name) synonym_name,
               lower(table_owner) table_owner,
               lower(table_name) table_name
        from user_synonyms
        where not exists (select null
                          from all_objects
                          where owner = user_synonyms.table_owner and
                                object_name = user_synonyms.table_name)
        order by lower(synonym_name);

    found_broken_synonyms boolean := false;
begin
    for broken_synonym in broken_synonyms
    loop
        found_broken_synonyms := true;

        dbms_output.put_line('Error: broken synonym: ' ||
                             broken_synonym.synonym_name || ' -> ' ||
                             broken_synonym.table_owner || '.' ||
                             broken_synonym.table_name);
    end loop;

    if found_broken_synonyms then
        :exit_status := 1;
    else
        :exit_status := 0;
    end if;
end;
/

exit :exit_status;
