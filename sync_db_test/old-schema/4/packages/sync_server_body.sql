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

create or replace package body sync_server as
    --------------------------------------------------------------------------
    -- Private constants, procedures and functions.
    --------------------------------------------------------------------------

    license_renewal_days number := 30;

    function check_device_license(
        device_uuid in varchar2
    ) return boolean is
        license_ok number;
    begin
        select count(*)
        into check_device_license.license_ok
        from device
             join device_license using (device_uuid)
        where device_uuid = check_device_license.device_uuid and
              (state != 'g' or
               license_expiry_time >= systimestamp +
                                      sync_server.license_renewal_days);

        return license_ok = 1;
    end;

    procedure update_device_license(
        device_uuid in varchar2
    ) is
        license_expiry_time device.license_expiry_time%type;
        state device_license.state%type;
    begin
        begin
            select license_expiry_time,
                   state
            into update_device_license.license_expiry_time,
                 update_device_license.state
            from device
                 left outer join device_license using (device_uuid)
            where device_uuid = update_device_license.device_uuid
            for update;
        exception
            when no_data_found then
                -- Device no longer exists, so there's nothing to do. This is
                -- not an error.
                return;
        end;

        if state is null then
            insert into device_license
            (
                device_uuid,
                state
            )
            values
            (
                update_device_license.device_uuid,
                'r'
            );
        elsif state = 'g' and
              license_expiry_time < systimestamp +
                                    sync_server.license_renewal_days then
            update device_license
            set state = 'e'
            where device_uuid = update_device_license.device_uuid;
        end if;
    end;

    --------------------------------------------------------------------------
    -- Public procedures and functions.
    --------------------------------------------------------------------------

    function get_device_secret(
        device_uuid in varchar2
    ) return varchar2 is
    begin
        -- TODO: temporary solution to avoid duplicating sync_admin code
        return sync_admin.get_device_secret(device_uuid);
    end;

    procedure get_device_state(
        device_uuid        in  varchar2,
        device_info        out sys_refcursor,
        device_config      out sys_refcursor,
        vm_instances       out sys_refcursor,
        vm_instance_config out sys_refcursor,
        vm_instance_disks  out sys_refcursor,
        disks              out sys_refcursor
    ) is
        license_ok boolean;
    begin
        set transaction read only;

        sync_util.check_database_state;
        sync_util.check_device_exists(device_uuid);

        -- TODO: Assumes license daemon and sync-server are in same time zone?
        open device_info for
            select release,
                   build,
                   repo_uuid,
                   file_size repo_file_size,
                   file_hash repo_file_hash,
                   to_char(from_tz(cast(license_expiry_time as timestamp),
                                   sessiontimezone),
                           'YYYY-MM-DD HH24:MI:SS TZHTZM') license_expiry_time,
                   license_hash
            from device
                 left outer join repo using (repo_uuid)
            where device_uuid = get_device_state.device_uuid;

        open device_config for
            select daemon,
                   key,
                   value
            from device_config
            where device_uuid = get_device_state.device_uuid
            order by daemon,
                     key;

        open vm_instances for
            select vm_instance_uuid,
                   vm_uuid,
                   vm_instance_name,
                   locked,
                   removed
            from vm_instance
            where device_uuid = get_device_state.device_uuid and
                  (removed = sync_util.false_char or
                   hard_removal = sync_util.false_char)
            order by vm_instance_uuid;

        open vm_instance_config for
            select vm_instance_uuid,
                   daemon,
                   key,
                   value
            from vm_instance
                 join vm_config using (vm_uuid)
            where device_uuid = get_device_state.device_uuid and
                  (removed = sync_util.false_char or
                   hard_removal = sync_util.false_char)
            order by vm_instance_uuid,
                     daemon,
                     key;

        open vm_instance_disks for
            select vm_instance_uuid,
                   disk_uuid
            from vm_instance
                 join vm_disk using (vm_uuid)
            where device_uuid = get_device_state.device_uuid and
                  (removed = sync_util.false_char or
                   hard_removal = sync_util.false_char)
            order by vm_instance_uuid,
                     disk_order;

        open disks for
            select distinct disk_uuid,
                            disk_name,
                            disk_type,
                            file_size,
                            file_hash,
                            encryption_key,
                            shared,
                            read_only
            from vm_instance
                 join vm_disk using (vm_uuid)
                 join disk using (disk_uuid)
            where device_uuid = get_device_state.device_uuid and
                  (removed = sync_util.false_char or
                   hard_removal = sync_util.false_char)
            order by disk_uuid;

        -- This check is not strictly necessary, since update_device_license
        -- performs the same check after locking the device and device_license
        -- row, but it avoids the overhead of locking the rows in the common
        -- case that the license doesn't need updating.
        license_ok := check_device_license(device_uuid);

        commit;

        if not license_ok then
            update_device_license(device_uuid);
        end if;

        commit;
    exception
        when others then
            rollback;
            raise;
    end;

    function get_disk_path(
        device_uuid in varchar2,
        disk_uuid   in varchar2
    ) return varchar2 is
        file_path disk.file_path%type;
    begin
        set transaction read only;

        sync_util.check_database_state;
        sync_util.check_device_exists(device_uuid);

        if disk_uuid is null then
            sync_error.raise(sync_error.disk_required);
        end if;

        begin
            select distinct file_path
            into get_disk_path.file_path
            from vm_instance
                 join vm_disk using (vm_uuid)
                 join disk using (disk_uuid)
            where device_uuid = get_disk_path.device_uuid and
                  disk_uuid = get_disk_path.disk_uuid and
                  (removed = sync_util.false_char or
                   hard_removal = sync_util.false_char);
        exception
            when no_data_found then
                -- Deliberately raise the same exception, regardless of
                -- whether the caller asks for a disk that doesn't exist or a
                -- disk that isn't in the device's target state.
                sync_error.raise(sync_error.disk_not_found,
                                 disk_uuid);
        end;

        commit;

        return file_path;
    exception
        when others then
            rollback;
            raise;
    end;

    function get_repo_path(
        device_uuid in varchar2,
        repo_uuid   in varchar2
    ) return varchar2 is
        file_path repo.file_path%type;
    begin
        set transaction read only;

        sync_util.check_database_state;
        sync_util.check_device_exists(device_uuid);

        if repo_uuid is null then
            sync_error.raise(sync_error.repo_required);
        end if;

        begin
            select distinct file_path
            into get_repo_path.file_path
            from device
                 join repo using (repo_uuid)
            where device_uuid = get_repo_path.device_uuid and
                  repo_uuid = get_repo_path.repo_uuid;
        exception
            when no_data_found then
                -- Deliberately raise the same exception, regardless of
                -- whether the caller asks for a repository file that doesn't
                -- exist or a file from a repository that isn't in the device's
                -- target state.
                sync_error.raise(sync_error.repo_not_found,
                                 repo_uuid);
        end;

        commit;

        return file_path;
    exception
        when others then
            rollback;
            raise;
    end;

    procedure report_device_state(
        device_uuid in varchar2,
        release     in varchar2,
        build       in varchar2
    ) is
        report_time timestamp(0) with local time zone;
    begin
        sync_util.check_database_state;

        sync_util.lock_device_row(device_uuid);

        report_time := systimestamp;

        begin
            update report_device
            set report_time = report_device_state.report_time,
                release = report_device_state.release,
                build = report_device_state.build
            where device_uuid = report_device_state.device_uuid;

            if sql%rowcount != 1 then
                insert into report_device
                (
                    device_uuid,
                    report_time,
                    release,
                    build
                )
                values
                (
                    report_device_state.device_uuid,
                    report_device_state.report_time,
                    report_device_state.release,
                    report_device_state.build
                );
            end if;
        exception
            when sync_error.value_too_large then
                case sync_error.get_violated_column
                    when 'report_device.release' then
                        sync_error.raise(sync_error.release_too_long,
                                         release);
                    when 'report_device.build' then
                        sync_error.raise(sync_error.build_too_long,
                                         build);
                    else
                        raise;
                end case;
        end;

        commit;
    exception
        when others then
            rollback;
            raise;
    end;
end;
/
