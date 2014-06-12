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

declare
    cursor sessions is
        select sid || ',' || serial# as id
        from v$session
        where username in (upper('&&sync_owner_user'),
                           upper('&&sync_admin_user'),
                           upper('&&sync_license_user'),
                           upper('&&sync_server_user'))
        order by username;

    cursor users is
        select username
        from all_users
        where username in (upper('&&sync_owner_user'),
                           upper('&&sync_admin_user'),
                           upper('&&sync_license_user'),
                           upper('&&sync_server_user'))
        order by username;

    killed_sessions boolean := false;
begin
    for session in sessions
    loop
        killed_sessions := true;
        execute immediate 'alter system kill session ''' || session.id || '''';
    end loop;

    if killed_sessions then
        dbms_lock.sleep(1);
    end if;

    for user in users
    loop
        execute immediate 'drop user ' || user.username || ' cascade';
    end loop;
end;
/
