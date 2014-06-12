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

create user &&sync_admin_user
    identified by &&sync_admin_password
    default tablespace users;

grant create session to &&sync_admin_user;
grant create synonym to &&sync_admin_user;

create user &&sync_license_user
    identified by &&sync_license_password
    default tablespace users;

grant create session to &&sync_license_user;
grant create synonym to &&sync_license_user;

create user &&sync_server_user
    identified by &&sync_server_password
    default tablespace users;

grant create session to &&sync_server_user;
grant create synonym to &&sync_server_user;
