/*
 * Copyright (c) 2012 Citrix Systems, Inc.
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

declare
    function table_exists(
        table_name in varchar2
    ) return boolean is
        num_matches number;
    begin
        select count(*)
        into table_exists.num_matches
        from user_tables
        where table_name = upper(table_exists.table_name);

        return num_matches = 1;
    end;

    function constraint_exists(
        constraint_name in varchar2
    ) return boolean is
        num_matches number;
    begin
        select count(*)
        into constraint_exists.num_matches
        from user_constraints
        where owner = user and
              constraint_name = upper(constraint_exists.constraint_name);

        return num_matches = 1;
    end;

begin
    if not table_exists('version') then
        execute immediate 
            'create table version
             (
                 current_version    varchar2(100),
                 installing_version varchar2(100)
             )';
    end if;

    if not constraint_exists('version_ck1') then
        execute immediate 
            'alter table version
                 add constraint version_ck1
                 check (current_version is not null or
                        installing_version is not null)';
    end if;
end;
/

lock table version in exclusive mode;

insert into version
select '1',
       '&&version'
from dual
where not exists (select null
                  from version);

commit;

-------------------------------------------------------------------------------
-- For upgrade from any schema version.
-------------------------------------------------------------------------------

update version
set installing_version = '&&version';

commit;
