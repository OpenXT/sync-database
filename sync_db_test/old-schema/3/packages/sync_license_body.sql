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

create or replace package body sync_license as
    --------------------------------------------------------------------------
    -- Public procedures and functions.
    --------------------------------------------------------------------------

    procedure deny_requested_license(
        device_uuid in varchar2
    ) is
    begin
        sync_util.check_database_state;

        delete from device_license
        where state = 'r' and
              device_uuid = deny_requested_license.device_uuid;

        if sql%rowcount != 1 then
            sync_error.raise(sync_error.requested_license_not_found,
                             device_uuid);
        end if;

        commit;
    exception
        when others then
            rollback;
            raise;
    end;

    procedure expire_random_licenses is
    begin
        sync_util.check_database_state;

        lock table device_license in exclusive mode;

        update device_license
        set state = 'e'
        where device_uuid in (select device_uuid
                              from (select device_uuid,
                                           rownum n
                                    from (select device_uuid
                                          from device_license
                                          where state = 'g'
                                          order by dbms_random.value))
                              where mod(n, 100) = 0);

        commit;
    exception
        when others then
            rollback;
            raise;
    end;

    procedure grant_requested_license(
        device_uuid         in varchar2,
        license_expiry_time in timestamp with local time zone,
        license_hash        in varchar2
    ) is
    begin
        sync_util.check_database_state;

        update device_license
        set state = 'g'
        where state = 'r' and
              device_uuid = grant_requested_license.device_uuid;

        if sql%rowcount != 1 then
            sync_error.raise(sync_error.requested_license_not_found,
                             device_uuid);
        end if;

        update device
        set license_expiry_time = grant_requested_license.license_expiry_time,
            license_hash = grant_requested_license.license_hash
        where device_uuid = grant_requested_license.device_uuid;

        if sql%rowcount != 1 then
            sync_error.raise(sync_error.device_not_found,
                             device_uuid);
        end if;

        commit;
    exception
        when others then
            rollback;
            raise;
    end;

    function lock_next_expired_license(
        prev_device_uuid in varchar2
    ) return varchar2 is
        device_uuid device_license.device_uuid%type;
    begin
        sync_util.check_database_state;

        begin
            select device_uuid
            into lock_next_expired_license.device_uuid
            from device_license
            where device_uuid = (
                select min(device_uuid)
                from device_license
                where state = 'e' and
                      (lock_next_expired_license.prev_device_uuid is null or
                       device_uuid >
                           lock_next_expired_license.prev_device_uuid))
            for update;
        exception
            when no_data_found then
                null;
        end;

        return device_uuid;
    exception
        when others then
            rollback;
            raise;
    end;

    function lock_next_requested_license(
        prev_device_uuid in varchar2
    ) return varchar2 is
        device_uuid device_license.device_uuid%type;
    begin
        sync_util.check_database_state;

        begin
            select device_uuid
            into lock_next_requested_license.device_uuid
            from device
                 join device_license using (device_uuid)
            where device_uuid = (
                select min(device_uuid)
                from device_license
                where state = 'r' and
                      (lock_next_requested_license.prev_device_uuid is null or
                       device_uuid >
                           lock_next_requested_license.prev_device_uuid))
            for update;
        exception
            when no_data_found then
                null;
        end;

        return device_uuid;
    exception
        when others then
            rollback;
            raise;
    end;

    procedure revoke_all_licenses is
    begin
        sync_util.check_database_state;

        lock table device_license in exclusive mode;

        update device_license
        set state = 'r'
        where state = 'g';

        delete from device_license
        where state = 'e';

        commit;
    exception
        when others then
            rollback;
            raise;
    end;

    procedure revoke_expired_license(
        device_uuid in varchar2
    ) is
    begin
        sync_util.check_database_state;

        delete from device_license
        where state = 'e' and
              device_uuid = revoke_expired_license.device_uuid;

        if sql%rowcount != 1 then
            sync_error.raise(sync_error.expired_license_not_found,
                             device_uuid);
        end if;

        commit;
    exception
        when others then
            rollback;
            raise;
    end;

    procedure skip_expired_license is
    begin
        sync_util.check_database_state;

        rollback;
    exception
        when others then
            rollback;
            raise;
    end;
end;
/
