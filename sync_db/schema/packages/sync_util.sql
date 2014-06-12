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

create or replace package sync_util as
    true_char constant varchar2(1) := 't';
    false_char constant varchar2(1) := 'f';

    function boolean_to_char(
        value in boolean
    ) return varchar2;

    procedure check_device_exists(
        device_uuid in varchar2,
        lock_row    in boolean := false
    );

    procedure check_database_state;

    function generate_uuid return varchar2;

    function get_num_offline_licenses(
        lock_row in boolean := false
    ) return varchar2;

    procedure lock_device_row(
        device_uuid in varchar2
    );
end;
/
