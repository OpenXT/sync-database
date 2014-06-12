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

variable exit_status number;

declare
    cursor invalid_objects_cursor is
        select object_name,
               object_type,
               status
        from user_objects
        where status != 'VALID'
        order by object_type,
                 object_name;

    cursor errors_cursor(
        object_name user_errors.name%type,
        object_type user_errors.type%type
    ) is
        select name,
               type,
               line,
               position,
               text
        from user_errors
        where name = errors_cursor.object_name and
              type = errors_cursor.object_type
        order by sequence;

    invalid_objects_error exception;
    found_invalid_objects boolean := false;
    error errors_cursor%rowtype;
begin
    for object in invalid_objects_cursor
    loop
        found_invalid_objects := true;

        dbms_output.put_line('Error: ' ||
                             lower(object.object_type) || ' ' ||
                             lower(object.object_name) || ' ' ||
                             lower(object.status) || '.');

        open errors_cursor(object.object_name, object.object_type);

        loop
            fetch errors_cursor into error;
            exit when errors_cursor%notfound;

            dbms_output.put_line('    ' ||
                                 error.line || '/' ||
                                 error.position || ': ' ||
                                 error.text);
        end loop;

        close errors_cursor;

        dbms_output.put_line('');
    end loop;

    if found_invalid_objects then
        :exit_status := 1;
    else
        :exit_status := 0;
    end if;
end;
/

exit :exit_status;
