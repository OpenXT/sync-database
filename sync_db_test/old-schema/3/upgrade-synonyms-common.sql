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

-------------------------------------------------------------------------------
-- For upgrade from schema version 1. Remove section when no longer needed.
-------------------------------------------------------------------------------

create or replace synonym version for &&sync_owner_user..version;

create or replace synonym sync_version for &&sync_owner_user..sync_version;

-------------------------------------------------------------------------------
-- For upgrade from schema version 2. Remove section when no longer needed.
-------------------------------------------------------------------------------

declare
    function synonym_exists(
        synonym_name in varchar2
    ) return boolean is
        num_matches number;
    begin
        select count(*)
        into synonym_exists.num_matches
        from user_synonyms
        where synonym_name = upper(synonym_exists.synonym_name);

        return num_matches = 1;
    end;
begin
    if synonym_exists('device_user') then
        execute immediate
            'drop synonym device_user';
    end if;

    if synonym_exists('user_') then
        execute immediate
            'drop synonym user_';
    end if;
end;
/
