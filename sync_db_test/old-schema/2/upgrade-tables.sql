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

declare
    function column_exists(
        table_name  in varchar2,
        column_name in varchar2
    ) return boolean is
        num_matches number;
    begin
        select count(*)
        into column_exists.num_matches
        from user_tab_columns
        where table_name = upper(column_exists.table_name) and
              column_name = upper(column_exists.column_name);

        return num_matches = 1;
    end;

    function get_column_length(
        table_name  in varchar2,
        column_name in varchar2
    ) return number is
        data_length number;
    begin
        select data_length
        into get_column_length.data_length
        from user_tab_columns
        where table_name = upper(get_column_length.table_name) and
              column_name = upper(get_column_length.column_name);

        return data_length;
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
    if not column_exists('disk', 'disk_type') then
        execute immediate
            'alter table disk add
             (
                 disk_type varchar2(1) default ''v'' not null,
                 read_only varchar2(1) default ''f'' not null
             )';
    end if;

    if not constraint_exists('disk_ck6') then
        execute immediate
            'alter table disk
                 add constraint disk_ck6
                 check (disk_type in (''i'', ''v''))';
    end if;

    if not constraint_exists('disk_ck7') then
        execute immediate
            'alter table disk
                 add constraint disk_ck7
                 check (not(disk_type = ''i'' and encryption_key is not null))';
    end if;

    if not constraint_exists('disk_ck8') then
        execute immediate
            'alter table disk
                 add constraint disk_ck8
                 check (read_only in (''t'', ''f''))';
    end if;

    if not constraint_exists('disk_ck9') then
        execute immediate
            'alter table disk
                 add constraint disk_ck9
                 check (not(disk_type = ''i'' and read_only = ''f''))';
    end if;

    if not constraint_exists('disk_ck10') then
        execute immediate
            'alter table disk
                 add constraint disk_ck10
                 check (not(shared = ''t'' and read_only = ''t''))';
    end if;

    if get_column_length('device_config', 'value') = 100 then
        execute immediate
            'alter table device_config modify
             (
                 value varchar2(3500)
             )';
    end if;

    if get_column_length('vm_config', 'value') = 100 then
        execute immediate
            'alter table vm_config modify
             (
                 value varchar2(3500)
             )';
    end if;
end;
/
