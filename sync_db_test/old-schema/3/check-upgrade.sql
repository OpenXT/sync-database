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
-- For upgrade from any schema version.
-------------------------------------------------------------------------------

variable exit_status number;

begin
    :exit_status := 0;
end;
/

-------------------------------------------------------------------------------
-- For upgrade from schema version 2. Remove section when no longer needed.
-------------------------------------------------------------------------------

declare
    cursor problems is
        select device_uuid,
               vm_uuid
        from vm_instance
        group by device_uuid,
                 vm_uuid
        having count(*) > 1;

    found_problems boolean := false;
begin
    for problem in problems
    loop
        if not found_problems then
            dbms_output.put_line('Error: Upgrade cannot proceed if multiple ' ||
                                 'users of a device have instances of the ' ||
                                 'same VM.');
            found_problems := true;
        end if;

        dbms_output.put_line('Device uuid ''' || problem.device_uuid || 
                             ''' has more than one instance of VM uuid ''' ||
                             problem.vm_uuid || '''.');
    end loop;

    if found_problems then
        :exit_status := 1;
    end if;
end;
/

-------------------------------------------------------------------------------
-- For upgrade from any schema version.
-------------------------------------------------------------------------------

exit :exit_status;
