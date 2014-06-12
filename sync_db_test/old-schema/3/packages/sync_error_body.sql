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

create or replace package body sync_error as
    --------------------------------------------------------------------------
    -- Public procedures and functions.
    --------------------------------------------------------------------------

    procedure raise(
        error_code in number,
        param1     in varchar2 := null,
        param2     in varchar2 := null,
        param3     in varchar2 := null,
        param4     in varchar2 := null
    ) is
        max_size constant number := 2048;
        message varchar2(2048);

        type params_list is varray(4) of varchar2(2048);
        params params_list := params_list(substrb(param1, 1, max_size),
                                          substrb(param2, 1, max_size),
                                          substrb(param3, 1, max_size),
                                          substrb(param4, 1, max_size));
    begin
        message := 'sync';

        for i in params.first .. params.last loop
            exit when params(i) is null;
            message :=
                substrb(message || '|' ||
                        translate(params(i), '|' || chr(10) || chr(13), '  '),
                        1,
                        max_size);
        end loop;

        raise_application_error(error_code, message);
    end;

    function get_violated_column return varchar2 is
    begin
        return lower(translate(regexp_substr(
                                   sqlerrm,
                                   '"[A-Z0-9_]+"\.("[A-Z0-9_]+"\."[A-Z0-9_]+")',
                                   1, 1, null, 1),
                               '_"', '_'));
    end;

    function get_violated_constraint return varchar2 is
    begin
        return lower(regexp_substr(sqlerrm,
                                   '\([A-Z0-9_]+\.([A-Z0-9_]+)\)',
                                   1, 1, null, 1));

    end;
end;
/
