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

create or replace package body sync_version as
    --------------------------------------------------------------------------
    -- Public procedures and functions.
    --------------------------------------------------------------------------

    procedure check_version(
        required_version in varchar2
    ) is
        current_version version.current_version%type;
    begin
        set transaction read only;

        sync_util.check_database_state;

        select current_version
        into check_version.current_version
        from version;

        if current_version != required_version then
            sync_error.raise(sync_error.db_version_incompatible,
                             current_version,
                             required_version);
        end if;

        commit;
    exception
        when others then
            rollback;
            raise;
    end;

    function get_version return varchar2 is
        current_version version.current_version%type;
    begin
        set transaction read only;

        sync_util.check_database_state;

        select current_version
        into get_version.current_version
        from version;

        commit;

        return current_version;
    exception
        when others then
            rollback;
            raise;
    end;
end;
/
