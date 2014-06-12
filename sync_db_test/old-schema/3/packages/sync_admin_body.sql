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

create or replace package body sync_admin as
    --------------------------------------------------------------------------
    -- Private constants, procedures and functions.
    --------------------------------------------------------------------------

    function boolean_to_char(
        value in boolean
    ) return varchar2 is
    begin
        if value then
            return sync_util.true_char;
        else
            return sync_util.false_char;
        end if;
    end;

    procedure check_file_size(
        file_size in number
    ) is
        test_file_size disk.file_size%type;
    begin
        test_file_size := file_size;
    exception
        when value_error then
            sync_error.raise(sync_error.file_size_invalid,
                             file_size);
    end;

    procedure check_disk_exists(
        disk_uuid in varchar2
    ) is
        dummy varchar2(1);
    begin
        if disk_uuid is null then
            sync_error.raise(sync_error.disk_required);
        end if;

        begin
            select null
            into check_disk_exists.dummy
            from disk
            where disk_uuid = check_disk_exists.disk_uuid;
        exception
            when no_data_found then
                sync_error.raise(sync_error.disk_not_found,
                                 disk_uuid);
        end;
    end;

    procedure check_repo_exists(
        repo_uuid in varchar2
    ) is
        dummy varchar2(1);
    begin
        if repo_uuid is null then
            sync_error.raise(sync_error.repo_required);
        end if;

        begin
            select null
            into check_repo_exists.dummy
            from repo
            where repo_uuid = check_repo_exists.repo_uuid;
        exception
            when no_data_found then
                sync_error.raise(sync_error.repo_not_found,
                                 repo_uuid);
        end;
    end;

    procedure check_vm_exists(
        vm_uuid  in varchar2,
        lock_row in boolean := false
    ) is
        dummy varchar2(1);
    begin
        if vm_uuid is null then
            sync_error.raise(sync_error.vm_required);
        end if;

        begin
            if lock_row then
                select null
                into check_vm_exists.dummy
                from vm
                where vm_uuid = check_vm_exists.vm_uuid
                for update;
            else
                select null
                into check_vm_exists.dummy
                from vm
                where vm_uuid = check_vm_exists.vm_uuid;
            end if;
        exception
            when no_data_found then
                sync_error.raise(sync_error.vm_not_found,
                                 vm_uuid);
        end;
    end;

    procedure check_vm_instance_exists(
        vm_instance_uuid in varchar2,
        lock_row         in boolean := false,
        allow_removed    in boolean := true
    ) is
        removed_char varchar2(1);
    begin
        if vm_instance_uuid is null then
            sync_error.raise(sync_error.vm_inst_required);
        end if;

        begin
            if lock_row then
                select removed
                into check_vm_instance_exists.removed_char
                from vm_instance
                where vm_instance_uuid =
                      check_vm_instance_exists.vm_instance_uuid
                for update;
            else
                select removed
                into check_vm_instance_exists.removed_char
                from vm_instance
                where vm_instance_uuid =
                      check_vm_instance_exists.vm_instance_uuid;
            end if;
        exception
            when no_data_found then
                sync_error.raise(sync_error.vm_inst_not_found,
                                 vm_instance_uuid);
        end;

        if not allow_removed and removed_char = sync_util.true_char then
            sync_error.raise(sync_error.vm_inst_removed,
                             vm_instance_uuid);
        end if;
    end;

    function escape_like(
        value varchar2
    ) return varchar2 is
    begin
        return replace(replace(replace(value, '!', '!!'),
                               '%', '!%'),
                       '_', '!_');
    end;

    function generate_uuid return varchar2 is
    begin
        return to_char(trunc(dbms_random.value(0, power(16, 8))),
                       'FM0xxxxxxx') || '-' ||
               to_char(trunc(dbms_random.value(0, power(16, 4))),
                       'FM0xxx') || '-' ||
               to_char(4 * power(16, 3) +
                       trunc(dbms_random.value(0, power(16, 3))),
                       'FM0xxx') || '-' ||
               to_char(8 * power(16, 3) +
                       trunc(dbms_random.value(0, 4 * power(16, 3))),
                       'FM0xxx') || '-' ||
               to_char(trunc(dbms_random.value(0, power(16, 12))),
                       'FM0xxxxxxxxxxx');
    end;

    function generate_secret return varchar2 is
    begin
        return to_char(dbms_crypto.randomnumber,
                       'FM0xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx');
    end;

    procedure split_config_item(
        config_item in  varchar2,
        daemon      out varchar2,
        key         out varchar2,
        value       out varchar2
    ) is
        sep_1 pls_integer;
        sep_2 pls_integer;
    begin
        if config_item is null then
            sync_error.raise(sync_error.config_empty);
        end if;

        sep_1 := instr(config_item, ':');
        sep_2 := instr(config_item, ':', sep_1 + 1);

        if sep_1 = 0 or sep_2 = 0 then
            sync_error.raise(sync_error.config_invalid,
                             config_item);
        end if;

        daemon := substr(config_item, 1, sep_1 - 1);
        key := substr(config_item, sep_1 + 1, sep_2 - sep_1 - 1);
        value := substr(config_item, sep_2 + 1);

        -- value is allowed to be null.
        if daemon is null or key is null then
            sync_error.raise(sync_error.config_invalid,
                             config_item);
        end if;
    end;

    procedure split_partial_config_item(
        config_item in  varchar2,
        daemon      out varchar2,
        key         out varchar2
    ) is
        sep_1 pls_integer;
        sep_2 pls_integer;
    begin
        if config_item is null then
            sync_error.raise(sync_error.config_empty);
        end if;

        sep_1 := instr(config_item, ':');
        sep_2 := instr(config_item, ':', sep_1 + 1);

        if sep_1 = 0 or sep_2 != 0 then
            sync_error.raise(sync_error.config_invalid,
                             config_item);
        end if;

        daemon := substr(config_item, 1, sep_1 - 1);
        key := substr(config_item, sep_1 + 1);

        if daemon is null or key is null then
            sync_error.raise(sync_error.config_invalid,
                             config_item);
        end if;
    end;

    procedure split_partial_config_list(
        config           in  varchar2_list,
        num_config_items in  number,
        daemons          out varchar2_list,
        keys             out varchar2_list
    ) is
        i pls_integer;
        j pls_integer;
    begin
        i := config.first;

        for j in 1..num_config_items loop
            if i is not null then
                split_partial_config_item(config(i),
                                          daemons(j),
                                          keys(j));
                i := config.next(i);
            else
                daemons(j) := null;
                keys(j) := null;
            end if;
        end loop;

        if i is not null then
            sync_error.raise(sync_error.too_many_config_items,
                             num_config_items);
        end if;
    end;

    procedure insert_device_config(
        device_uuid in varchar2,
        config      in varchar2_list
    ) is
        i pls_integer;

        -- If daemon, key or value is too long, we want the exception to be
        -- raised on insert rather than in split_config_item, so allocate
        -- large buffers for them.
        daemon varchar2(4000);
        key varchar2(4000);
        value varchar2(4000);
    begin
        i := config.first;

        while i is not null loop
            split_config_item(config(i),
                              daemon,
                              key,
                              value);

            delete from device_config
            where device_uuid = insert_device_config.device_uuid and
                  daemon = insert_device_config.daemon and
                  key = insert_device_config.key;

            if value is not null then
                begin
                    insert into device_config
                    (
                        device_uuid,
                        daemon,
                        key,
                        value
                    )
                    values
                    (
                        device_uuid,
                        daemon,
                        key,
                        value
                    );
                exception
                    when sync_error.value_too_large then
                        case sync_error.get_violated_column
                            when 'device_config.daemon' then
                                sync_error.raise(
                                    sync_error.config_daemon_too_long,
                                    daemon);
                            when 'device_config.key' then
                                sync_error.raise(
                                    sync_error.config_key_too_long,
                                    key);
                            when 'device_config.value' then
                                sync_error.raise(
                                    sync_error.config_value_too_long,
                                    value);
                            else
                                raise;
                        end case;
                end;
            end if;

            i := config.next(i);
        end loop;
    end;

    procedure insert_vm_config(
        vm_uuid in varchar2,
        config  in varchar2_list
    ) is
        i pls_integer;

        -- If daemon, key or value is too long, we want the exception to be
        -- raised on insert rather than in split_config_item, so allocate
        -- large buffers for them.
        daemon varchar2(4000);
        key varchar2(4000);
        value varchar2(4000);
    begin
        i := config.first;

        while i is not null loop
            split_config_item(config(i),
                              daemon,
                              key,
                              value);

            delete from vm_config
            where vm_uuid = insert_vm_config.vm_uuid and
                  daemon = insert_vm_config.daemon and
                  key = insert_vm_config.key;

            if value is not null then
                begin
                    insert into vm_config
                    (
                        vm_uuid,
                        daemon,
                        key,
                        value
                    )
                    values
                    (
                        vm_uuid,
                        daemon,
                        key,
                        value
                    );
                exception
                    when sync_error.value_too_large then
                        case sync_error.get_violated_column
                            when 'vm_config.daemon' then
                                sync_error.raise(
                                    sync_error.config_daemon_too_long,
                                    daemon);
                            when 'vm_config.key' then
                                sync_error.raise(
                                    sync_error.config_key_too_long,
                                    key);
                            when 'vm_config.value' then
                                sync_error.raise(
                                    sync_error.config_value_too_long,
                                    value);
                            else
                                raise;
                        end case;
                end;
            end if;

            i := config.next(i);
        end loop;
    end;

    procedure insert_vm_disks(
        vm_uuid    in varchar2,
        disk_uuids in varchar2_list
    ) is
        i pls_integer;
        disk_order vm_disk.disk_order%type;
    begin
        i := disk_uuids.first;
        disk_order := 1;

        while i is not null loop
            begin
                insert into vm_disk
                (
                    vm_uuid,
                    disk_uuid,
                    disk_order
                )
                values
                (
                    vm_uuid,
                    disk_uuids(i),
                    disk_order
                );
            exception
                when dup_val_on_index then
                    case sync_error.get_violated_constraint
                        when 'vm_disk_pk' then
                            sync_error.raise(sync_error.disk_repeated,
                                             disk_uuids(i));
                        else
                            raise;
                    end case;

                when sync_error.cannot_insert_null then
                    case sync_error.get_violated_column
                        when 'vm_disk.disk_uuid' then
                            sync_error.raise(sync_error.disk_required);
                        else
                            raise;
                    end case;

                when sync_error.parent_key_not_found then
                    case sync_error.get_violated_constraint
                        when 'vm_disk_fk2' then
                            sync_error.raise(sync_error.disk_not_found,
                                             disk_uuids(i));
                        else
                            raise;
                    end case;

                when sync_error.value_too_large then
                    case sync_error.get_violated_column
                        when 'vm_disk.disk_uuid' then
                            sync_error.raise(sync_error.disk_not_found,
                                             disk_uuids(i));
                        else
                            raise;
                    end case;
            end;

            i := disk_uuids.next(i);
            disk_order := disk_order + 1;
        end loop;
    end;

    procedure lock_unremoved_vm_instance_row(
        vm_instance_uuid in varchar2
    ) is
    begin
        check_vm_instance_exists(vm_instance_uuid, true, false);
    end;

    procedure lock_vm_row(
        vm_uuid in varchar2
    ) is
    begin
        check_vm_exists(vm_uuid, true);
    end;

    procedure lock_vm_instance_row(
        vm_instance_uuid in varchar2
    ) is
    begin
        check_vm_instance_exists(vm_instance_uuid, true, true);
    end;

    function partial_uuid_is_valid(
        partial_uuid in varchar2
    ) return boolean is
    begin
        return partial_uuid is null or
               translate(partial_uuid, '_0123456789abcdef-', '_') is null;
    end;

    --------------------------------------------------------------------------
    -- Public procedures and functions.
    --------------------------------------------------------------------------

    function add_device(
        device_name in varchar2,
        repo_uuid   in varchar2,
        config      in varchar2_list
    ) return varchar2 is
        device_uuid device.device_uuid%type;
        shared_secret device.shared_secret%type;
    begin
        sync_util.check_database_state;

        device_uuid := generate_uuid;
        shared_secret := generate_secret;

        begin
            insert into device
            (
                device_uuid,
                device_name,
                shared_secret,
                repo_uuid,
                license_expiry_time,
                license_hash
            )
            values
            (
                device_uuid,
                device_name,
                shared_secret,
                repo_uuid,
                null,
                null
            );
        exception
            when sync_error.cannot_insert_null then
                case sync_error.get_violated_column
                    when 'device.device_name' then
                        sync_error.raise(sync_error.device_name_required);
                    else
                        raise;
                end case;

            when sync_error.parent_key_not_found then
                case sync_error.get_violated_constraint
                    when 'device_fk1' then
                        sync_error.raise(sync_error.repo_not_found,
                                         repo_uuid);
                    else
                        raise;
                end case;

            when sync_error.value_too_large then
                case sync_error.get_violated_column
                    when 'device.device_name' then
                        sync_error.raise(sync_error.device_name_too_long,
                                         device_name);
                    when 'device.repo_uuid' then
                        sync_error.raise(sync_error.repo_not_found,
                                         repo_uuid);
                    else
                        raise;
                end case;
        end;

        insert_device_config(device_uuid, config);

        commit;

        return device_uuid;
    exception
        when others then
            rollback;
            raise;
    end;

    function add_disk(
        disk_name      in varchar2,
        disk_type      in varchar2,
        file_path      in varchar2,
        file_size      in number,
        file_hash      in varchar2,
        encryption_key in varchar2,
        shared         in boolean,
        read_only      in boolean
    ) return varchar2 is
        disk_uuid disk.disk_uuid%type;
        shared_char disk.shared%type;
        read_only_char disk.read_only%type;
    begin
        sync_util.check_database_state;
        check_file_size(file_size);

        disk_uuid := generate_uuid;
        shared_char := boolean_to_char(shared);
        read_only_char := boolean_to_char(read_only);

        begin
            insert into disk
            (
                disk_uuid,
                disk_name,
                disk_type,
                file_path,
                file_size,
                file_hash,
                encryption_key,
                shared,
                read_only
            )
            values
            (
                disk_uuid,
                disk_name,
                disk_type,
                file_path,
                file_size,
                file_hash,
                encryption_key,
                shared_char,
                read_only_char
            );
        exception
            when dup_val_on_index then
                case sync_error.get_violated_constraint
                    when 'disk_uk1' then
                        sync_error.raise(sync_error.file_path_not_unique,
                                         file_path);
                    else
                        raise;
                end case;

            when sync_error.cannot_insert_null then
                case sync_error.get_violated_column
                    when 'disk.disk_name' then
                        sync_error.raise(sync_error.disk_name_required);
                    when 'disk.file_path' then
                        sync_error.raise(sync_error.file_path_required);
                    when 'disk.file_size' then
                        sync_error.raise(sync_error.file_size_required);
                    when 'disk.file_hash' then
                        sync_error.raise(sync_error.file_hash_required);
                    else
                        raise;
                end case;

            when sync_error.check_constraint_violated then
                case sync_error.get_violated_constraint
                    when 'disk_ck2' then
                        sync_error.raise(sync_error.file_size_invalid,
                                         file_size);
                    when 'disk_ck3' then
                        sync_error.raise(sync_error.file_hash_invalid,
                                         file_hash);
                    when 'disk_ck4' then
                        -- Don't include encryption key in error message.
                        sync_error.raise(sync_error.encryption_key_invalid);
                    when 'disk_ck6' then
                        sync_error.raise(sync_error.disk_type_invalid,
                                         disk_type);
                    when 'disk_ck7' then
                        sync_error.raise(sync_error.iso_with_encryption_key);
                    when 'disk_ck9' then
                        sync_error.raise(sync_error.iso_not_read_only);
                    when 'disk_ck10' then
                        sync_error.raise(sync_error.disk_read_only_and_shared);
                    else
                        raise;
                end case;

            when sync_error.value_too_large then
                case sync_error.get_violated_column
                    when 'disk.disk_name' then
                        sync_error.raise(sync_error.disk_name_too_long,
                                         disk_name);
                    when 'disk.file_path' then
                        sync_error.raise(sync_error.file_path_too_long,
                                         file_path);
                    when 'disk.file_hash' then
                        sync_error.raise(sync_error.file_hash_invalid,
                                         file_hash);
                    when 'disk.encryption_key' then
                        -- Don't include encryption key in error message.
                        sync_error.raise(sync_error.encryption_key_invalid);
                    else
                        raise;
                end case;
        end;

        commit;

        return disk_uuid;
    exception
        when others then
            rollback;
            raise;
    end;

    function add_repo(
        release    in varchar2,
        build      in varchar2,
        file_path  in varchar2,
        file_size  in number,
        file_hash in varchar2
    ) return varchar2 is
        repo_uuid repo.repo_uuid%type;
    begin
        sync_util.check_database_state;
        check_file_size(file_size);

        repo_uuid := generate_uuid;

        begin
            insert into repo
            (
                repo_uuid,
                release,
                build,
                file_path,
                file_size,
                file_hash
            )
            values
            (
                repo_uuid,
                release,
                build,
                file_path,
                file_size,
                file_hash
            );
        exception
            when dup_val_on_index then
                case sync_error.get_violated_constraint
                    when 'repo_uk1' then
                        sync_error.raise(sync_error.file_path_not_unique,
                                         file_path);
                    when 'repo_uk2' then
                        sync_error.raise(sync_error.repo_exists,
                                         release,
                                         build);
                    else
                        raise;
                end case;

            when sync_error.cannot_insert_null then
                case sync_error.get_violated_column
                    when 'repo.release' then
                        sync_error.raise(sync_error.release_required);
                    when 'repo.build' then
                        sync_error.raise(sync_error.build_required);
                    when 'repo.file_path' then
                        sync_error.raise(sync_error.file_path_required);
                    when 'repo.file_size' then
                        sync_error.raise(sync_error.file_size_required);
                    when 'repo.file_hash' then
                        sync_error.raise(sync_error.file_hash_required);
                    else
                        raise;
                end case;

            when sync_error.check_constraint_violated then
                case sync_error.get_violated_constraint
                    when 'repo_ck2' then
                        sync_error.raise(sync_error.file_size_invalid,
                                         file_size);
                    when 'repo_ck3' then
                        sync_error.raise(sync_error.file_hash_invalid,
                                         file_hash);
                    else
                        raise;
                end case;

            when sync_error.value_too_large then
                case sync_error.get_violated_column
                    when 'repo.release' then
                        sync_error.raise(sync_error.release_too_long,
                                         release);
                    when 'repo.build' then
                        sync_error.raise(sync_error.build_too_long,
                                         build);
                    when 'repo.file_path' then
                        sync_error.raise(sync_error.file_path_too_long,
                                         file_path);
                    when 'repo.file_hash' then
                        sync_error.raise(sync_error.file_hash_invalid,
                                         file_hash);
                    else
                        raise;
                end case;
        end;

        commit;

        return repo_uuid;
    exception
        when others then
            rollback;
            raise;
    end;

    function add_vm(
        vm_name    in varchar2,
        disk_uuids in varchar2_list,
        config     in varchar2_list
    ) return varchar2 is
        vm_uuid vm.vm_uuid%type;
    begin
        sync_util.check_database_state;

        vm_uuid := generate_uuid;

        begin
            insert into vm
            (
                vm_uuid,
                vm_name
            )
            values
            (
                vm_uuid,
                vm_name
            );
        exception
            when sync_error.cannot_insert_null then
                case sync_error.get_violated_column
                    when 'vm.vm_name' then
                        sync_error.raise(sync_error.vm_name_required);
                    else
                        raise;
                end case;

            when sync_error.value_too_large then
                case sync_error.get_violated_column
                    when 'vm.vm_name' then
                        sync_error.raise(sync_error.vm_name_too_long,
                                         vm_name);
                    else
                        raise;
                end case;
        end;

        insert_vm_disks(vm_uuid, disk_uuids);
        insert_vm_config(vm_uuid, config);

        commit;

        return vm_uuid;
    exception
        when others then
            rollback;
            raise;
    end;

    function add_vm_instance(
        device_uuid      in varchar2,
        vm_uuid          in varchar2,
        vm_instance_name in varchar2
    ) return varchar2 is
        vm_instance_uuid vm_instance.vm_instance_uuid%type;
        duplicate_key boolean := false;
        removed_char varchar2(1);
    begin
        sync_util.check_database_state;

        sync_util.lock_device_row(device_uuid);

        vm_instance_uuid := generate_uuid;

        begin
            insert into vm_instance
            (
                vm_instance_uuid,
                device_uuid,
                vm_uuid,
                vm_instance_name,
                locked,
                removed
            )
            values
            (
                vm_instance_uuid,
                device_uuid,
                vm_uuid,
                vm_instance_name,
                sync_util.false_char,
                sync_util.false_char
            );
        exception
            when dup_val_on_index then
                case sync_error.get_violated_constraint
                    when 'vm_instance_uk1' then
                        duplicate_key := true;
                    else
                        raise;
                end case;

            when sync_error.cannot_insert_null then
                case sync_error.get_violated_column
                    when 'vm_instance.vm_uuid' then
                        sync_error.raise(sync_error.vm_required);
                    when 'vm_instance.vm_instance_name' then
                        sync_error.raise(sync_error.vm_inst_name_required);
                    else
                        raise;
                end case;

            when sync_error.parent_key_not_found then
                case sync_error.get_violated_constraint
                    when 'vm_instance_fk2' then
                        sync_error.raise(sync_error.vm_not_found,
                                         vm_uuid);
                    else
                        raise;
                end case;

            when sync_error.value_too_large then
                case sync_error.get_violated_column
                    when 'vm_instance.vm_uuid' then
                        sync_error.raise(sync_error.vm_not_found,
                                         vm_uuid);
                    when 'vm_instance.vm_instance_name' then
                        sync_error.raise(sync_error.vm_inst_name_too_long,
                                         vm_instance_name);
                    else
                        raise;
                end case;
        end;

        if duplicate_key then
            select vm_instance_uuid,
                   removed
            into add_vm_instance.vm_instance_uuid,
                 add_vm_instance.removed_char
            from vm_instance
            where device_uuid = add_vm_instance.device_uuid and
                  vm_uuid = add_vm_instance.vm_uuid;

            if removed_char = sync_util.true_char then
                sync_error.raise(sync_error.removed_vm_inst_exists,
                                 vm_instance_uuid,
                                 device_uuid,
                                 vm_uuid);
            else
                sync_error.raise(sync_error.vm_inst_exists,
                                 vm_instance_uuid,
                                 device_uuid,
                                 vm_uuid);
            end if;
        end if;

        commit;

        return vm_instance_uuid;
    exception
        when others then
            rollback;
            raise;
    end;

    function complete_device_uuid(
        partial_device_uuid in varchar2
    ) return sys_refcursor is
        device_uuids sys_refcursor;
    begin
        set transaction read only;

        sync_util.check_database_state;

        if partial_uuid_is_valid(partial_device_uuid) then
            open device_uuids for
                select device_uuid
                from device
                where device_uuid like partial_device_uuid || '%'
                order by device_uuid;
        else
            open device_uuids for
                select device_uuid
                from device
                where 1 = 0;
        end if;

        commit;

        return device_uuids;
    exception
        when others then
            rollback;
            raise;
    end;

    function complete_disk_uuid(
        partial_disk_uuid in varchar2
    ) return sys_refcursor is
        disk_uuids sys_refcursor;
    begin
        set transaction read only;

        sync_util.check_database_state;

        if partial_uuid_is_valid(partial_disk_uuid) then
            open disk_uuids for
                select disk_uuid
                from disk
                where disk_uuid like partial_disk_uuid || '%'
                order by disk_uuid;
        else
            open disk_uuids for
                select disk_uuid
                from disk
                where 1 = 0;
        end if;

        commit;

        return disk_uuids;
    exception
        when others then
            rollback;
            raise;
    end;

    function complete_repo_uuid(
        partial_repo_uuid in varchar2
    ) return sys_refcursor is
        repo_uuids sys_refcursor;
    begin
        set transaction read only;

        sync_util.check_database_state;

        if partial_uuid_is_valid(partial_repo_uuid) then
            open repo_uuids for
                select repo_uuid
                from repo
                where repo_uuid like partial_repo_uuid || '%'
                order by repo_uuid;
        else
            open repo_uuids for
                select repo_uuid
                from repo
                where 1 = 0;
        end if;

        commit;

        return repo_uuids;
    exception
        when others then
            rollback;
            raise;
    end;

    function complete_vm_uuid(
        partial_vm_uuid in varchar2
    ) return sys_refcursor is
        vm_uuids sys_refcursor;
    begin
        set transaction read only;

        sync_util.check_database_state;

        if partial_uuid_is_valid(partial_vm_uuid) then
            open vm_uuids for
                select vm_uuid
                from vm
                where vm_uuid like partial_vm_uuid || '%'
                order by vm_uuid;
        else
            open vm_uuids for
                select vm_uuid
                from vm
                where 1 = 0;
        end if;

        commit;

        return vm_uuids;
    exception
        when others then
            rollback;
            raise;
    end;

    function complete_vm_instance_uuid(
        partial_vm_instance_uuid in varchar2,
        include_unremoved        in boolean,
        include_removed          in boolean
    ) return sys_refcursor is
        vm_instance_uuids sys_refcursor;
        removed_char_1 varchar2(1);
        removed_char_2 varchar2(1);
    begin
        set transaction read only;

        sync_util.check_database_state;

        if partial_uuid_is_valid(partial_vm_instance_uuid) then
            if include_unremoved then
                removed_char_1 := sync_util.false_char;
            end if;

            if include_removed then
                removed_char_2 := sync_util.true_char;
            end if;

            open vm_instance_uuids for
                select vm_instance_uuid
                from vm_instance
                where vm_instance_uuid like partial_vm_instance_uuid || '%' and
                      removed in (removed_char_1, removed_char_2)
                order by vm_instance_uuid;
        else
            open vm_instance_uuids for
                select vm_instance_uuid
                from vm_instance
                where 1 = 0;
        end if;

        commit;

        return vm_instance_uuids;
    exception
        when others then
            rollback;
            raise;
    end;

    function get_device(
        device_uuid in varchar2
    ) return sys_refcursor is
        device_cursor sys_refcursor;
    begin
        set transaction read only;

        sync_util.check_database_state;
        sync_util.check_device_exists(device_uuid);

        -- The shared_secret column is intentionally excluded from the query.
        -- It should be fetched explicitly with get_device_secret.
        open device_cursor for
            select device_uuid,
                   device_name,
                   repo_uuid
            from device
            where device_uuid = get_device.device_uuid;

        commit;

        return device_cursor;
    exception
        when others then
            rollback;
            raise;
    end;

    function get_device_config(
        device_uuid in varchar2
    ) return sys_refcursor is
        config_cursor sys_refcursor;
    begin
        set transaction read only;

        sync_util.check_database_state;
        sync_util.check_device_exists(device_uuid);

        open config_cursor for
            select daemon,
                   key,
                   value
            from device_config
            where device_uuid = get_device_config.device_uuid
            order by daemon,
                     key;

        commit;

        return config_cursor;
    exception
        when others then
            rollback;
            raise;
    end;

    function get_device_secret(
        device_uuid in varchar2
    ) return varchar2 is
        shared_secret device.shared_secret%type;
    begin
        set transaction read only;

        sync_util.check_database_state;

        if device_uuid is null then
            sync_error.raise(sync_error.device_required);
        end if;

        begin
            select shared_secret
            into get_device_secret.shared_secret
            from device
            where device_uuid = get_device_secret.device_uuid;
        exception
            when no_data_found then
                sync_error.raise(sync_error.device_not_found,
                                 device_uuid);
        end;

        commit;

        return shared_secret;
    exception
        when others then
            rollback;
            raise;
    end;

    function get_disk(
        disk_uuid in varchar2
    ) return sys_refcursor is
        disk_cursor sys_refcursor;
    begin
        set transaction read only;

        sync_util.check_database_state;
        check_disk_exists(disk_uuid);

        -- The encryption_key column is intentionally excluded from the query.
        -- It should be fetched explicitly with get_disk_key.
        open disk_cursor for
            select disk_uuid,
                   disk_name,
                   disk_type,
                   file_path,
                   file_size,
                   file_hash,
                   shared,
                   read_only
            from disk
            where disk_uuid = get_disk.disk_uuid;

        commit;

        return disk_cursor;
    exception
        when others then
            rollback;
            raise;
    end;

    function get_disk_key(
        disk_uuid in varchar2
    ) return varchar2 is
        encryption_key disk.encryption_key%type;
    begin
        set transaction read only;

        sync_util.check_database_state;

        if disk_uuid is null then
            sync_error.raise(sync_error.disk_required);
        end if;

        begin
            select encryption_key
            into get_disk_key.encryption_key
            from disk
            where disk_uuid = get_disk_key.disk_uuid;
        exception
            when no_data_found then
                sync_error.raise(sync_error.disk_not_found,
                                 disk_uuid);
        end;

        commit;

        return encryption_key;
    exception
        when others then
            rollback;
            raise;
    end;

    function get_repo(
        repo_uuid in varchar2
    ) return sys_refcursor is
        repo_cursor sys_refcursor;
    begin
        set transaction read only;

        sync_util.check_database_state;
        check_repo_exists(repo_uuid);

        open repo_cursor for
            select repo_uuid,
                   release,
                   build,
                   file_path,
                   file_size,
                   file_hash
            from repo
            where repo_uuid = get_repo.repo_uuid;

        commit;

        return repo_cursor;
    exception
        when others then
            rollback;
            raise;
    end;

    function get_report(
        device_uuid in varchar2
    ) return sys_refcursor is
        device_report_cursor sys_refcursor;
    begin
        set transaction read only;

        sync_util.check_database_state;
        sync_util.check_device_exists(device_uuid);

        open device_report_cursor for
            select device_uuid,
                   report_time,
                   release,
                   build
            from device
                 left outer join report_device using (device_uuid)
            where device_uuid = get_report.device_uuid;

        commit;

        return device_report_cursor;
    exception
        when others then
            rollback;
            raise;
    end;

    function get_vm(
        vm_uuid in varchar2
    ) return sys_refcursor is
        vm_cursor sys_refcursor;
    begin
        set transaction read only;

        sync_util.check_database_state;
        check_vm_exists(vm_uuid);

        open vm_cursor for
            select vm_uuid,
                   vm_name
            from vm
            where vm_uuid = get_vm.vm_uuid;

        commit;

        return vm_cursor;
    exception
        when others then
            rollback;
            raise;
    end;

    function get_vm_config(
        vm_uuid in varchar2
    ) return sys_refcursor is
        config_cursor sys_refcursor;
    begin
        set transaction read only;

        sync_util.check_database_state;
        check_vm_exists(vm_uuid);

        open config_cursor for
            select daemon,
                   key,
                   value
            from vm_config
            where vm_uuid = get_vm_config.vm_uuid
            order by daemon,
                     key;

        commit;

        return config_cursor;
    end;

    function get_vm_instance(
        vm_instance_uuid in varchar2
    ) return sys_refcursor is
        vm_instance_cursor sys_refcursor;
    begin
        set transaction read only;

        sync_util.check_database_state;
        check_vm_instance_exists(vm_instance_uuid);

        open vm_instance_cursor for
            select vm_instance_uuid,
                   device_uuid,
                   vm_uuid,
                   vm_instance_name,
                   locked,
                   removed
            from vm_instance
            where vm_instance_uuid = get_vm_instance.vm_instance_uuid;

        commit;

        return vm_instance_cursor;
    exception
        when others then
            rollback;
            raise;
    end;

    procedure list_all_files(
        disks out sys_refcursor,
        repos out sys_refcursor
    ) is
    begin
        set transaction read only;

        sync_util.check_database_state;

        open disks for
            select disk_uuid,
                   file_path,
                   file_size,
                   file_hash
            from disk
            order by disk_uuid;

        open repos for
            select repo_uuid,
                   file_path,
                   file_size,
                   file_hash
            from repo
            order by repo_uuid;

        commit;
    exception
        when others then
            rollback;
            raise;
    end;

    function list_devices(
        device_name in varchar2,
        repo_uuid   in varchar2,
        no_repo     in boolean,
        vm_uuid     in varchar2
    ) return sys_refcursor is
        devices sys_refcursor;
    begin
        set transaction read only;

        sync_util.check_database_state;

        -- Check that no more than one filter is specified.
        if (case when device_name is not null then 1 else 0 end) +
           (case when repo_uuid   is not null then 1 else 0 end) +
           (case when no_repo                 then 1 else 0 end) +
           (case when vm_uuid     is not null then 1 else 0 end) > 1 then
            sync_error.raise(sync_error.multiple_filters);
        end if;

        -- The shared_secret column is intentionally excluded from the query.
        -- It should be fetched explicitly with get_device_secret.
        if device_name is not null then
            open devices for
                select device_uuid,
                       device_name
                from device
                where device_name = list_devices.device_name
                order by device_uuid;
        elsif repo_uuid is not null then
            check_repo_exists(repo_uuid);

            open devices for
                select device_uuid,
                       device_name
                from device
                where repo_uuid = list_devices.repo_uuid
                order by device_uuid;
        elsif no_repo then
            open devices for
                select device_uuid,
                       device_name
                from device
                where repo_uuid is null
                order by device_uuid;
        elsif vm_uuid is not null then
            check_vm_exists(vm_uuid);

            open devices for
                select distinct device_uuid,
                                device_name
                from device
                     join vm_instance using (device_uuid)
                where vm_uuid = list_devices.vm_uuid and
                      vm_instance.removed = sync_util.false_char
                order by device_uuid;
        else
            open devices for
                select device_uuid,
                       device_name
                from device
                order by device_uuid;
        end if;

        commit;

        return devices;
    exception
        when others then
            rollback;
            raise;
    end;

    function list_devices_ui(
        device_name_contains in varchar2
    ) return sys_refcursor is
        pattern varchar2(2048);
        devices sys_refcursor;
    begin
        set transaction read only;

        if device_name_contains is not null then
            pattern := '%' ||
                       escape_like(lower(
                            list_devices_ui.device_name_contains)) || '%';
        end if;

        open devices for
            select device_uuid,
                   device_name,
                   report_time
            from device
                 left outer join report_device using (device_uuid)
            where pattern is null or
                  lower(device_name) like pattern escape '!'
            order by device_uuid;

        commit;

        return devices;
    exception
        when others then
            rollback;
            raise;
    end;

    function list_disks(
        disk_name        in varchar2,
        disk_type        in varchar2,
        file_path        in varchar2,
        file_hash        in varchar2,
        vm_uuid          in varchar2,
        vm_instance_uuid in varchar2,
        unused           in boolean
    ) return sys_refcursor is
        disks sys_refcursor;
    begin
        set transaction read only;

        sync_util.check_database_state;

        -- Check that no more than one filter is specified.
        if (case when disk_name        is not null then 1 else 0 end) +
           (case when disk_type        is not null then 1 else 0 end) +
           (case when file_path        is not null then 1 else 0 end) +
           (case when file_hash        is not null then 1 else 0 end) +
           (case when vm_uuid          is not null then 1 else 0 end) +
           (case when vm_instance_uuid is not null then 1 else 0 end) +
           (case when unused                       then 1 else 0 end) > 1 then
            sync_error.raise(sync_error.multiple_filters);
        end if;

        -- The encryption_key column is intentionally excluded from the query.
        -- It should be fetched explicitly with get_disk_key.
        if disk_name is not null then
            open disks for
                select disk_uuid,
                       disk_name,
                       disk_type,
                       file_path
                from disk
                where disk_name = list_disks.disk_name
                order by disk_uuid;
        elsif disk_type is not null then
            open disks for
                select disk_uuid,
                       disk_name,
                       disk_type,
                       file_path
                from disk
                where disk_type = list_disks.disk_type
                order by disk_uuid;
        elsif file_path is not null then
            open disks for
                select disk_uuid,
                       disk_name,
                       disk_type,
                       file_path
                from disk
                where file_path = list_disks.file_path
                order by disk_uuid;
        elsif file_hash is not null then
            open disks for
                select disk_uuid,
                       disk_name,
                       disk_type,
                       file_path
                from disk
                where file_hash = list_disks.file_hash
                order by disk_uuid;
        elsif vm_uuid is not null then
            check_vm_exists(vm_uuid);

            open disks for
                select disk_uuid,
                       disk_name,
                       disk_type,
                       file_path,
                       disk_order
                from disk
                     join vm_disk using (disk_uuid)
                where vm_uuid = list_disks.vm_uuid
                order by disk_order;
        elsif vm_instance_uuid is not null then
            check_vm_instance_exists(vm_instance_uuid);

            open disks for
                select disk_uuid,
                       disk_name,
                       disk_type,
                       file_path,
                       disk_order
                from disk
                     join vm_disk using (disk_uuid)
                     join vm_instance using (vm_uuid)
                where vm_instance_uuid = list_disks.vm_instance_uuid
                order by disk_order;
        elsif unused then
            open disks for
                select disk_uuid,
                       disk_name,
                       disk_type,
                       file_path
                from disk
                where disk_uuid not in (select disk_uuid
                                        from vm_disk)
                order by disk_uuid;
        else
            open disks for
                select disk_uuid,
                       disk_name,
                       disk_type,
                       file_path
                from disk
                order by disk_uuid;
        end if;

        commit;

        return disks;
    exception
        when others then
            rollback;
            raise;
    end;

    function list_disks_ui(
        disk_name_contains in varchar2
    ) return sys_refcursor is
        pattern varchar2(2048);
        disks sys_refcursor;
    begin
        set transaction read only;

        if disk_name_contains is not null then
            pattern := '%' ||
                       escape_like(lower(
                            list_disks_ui.disk_name_contains)) || '%';
        end if;

        open disks for
            select disk_uuid,
                   disk_name,
                   disk_type,
                   file_path,
                   shared,
                   read_only,
                   count(vm_uuid) num_vms
            from disk
                 left outer join vm_disk using (disk_uuid)
            where pattern is null or
                  lower(disk_name) like pattern escape '!'
            group by disk_uuid,
                     disk_name,
                     disk_type,
                     file_path,
                     shared,
                     read_only
            order by disk_uuid;

        commit;

        return disks;
    exception
        when others then
            rollback;
            raise;
    end;

    function list_repos(
        release   in varchar2,
        build     in varchar2,
        file_path in varchar2,
        file_hash in varchar2,
        unused    in boolean
    ) return sys_refcursor is
        repos sys_refcursor;
    begin
        set transaction read only;

        sync_util.check_database_state;

        -- Check that no more than one filter is specified.
        if (case when release   is not null then 1 else 0 end) +
           (case when build     is not null then 1 else 0 end) +
           (case when file_path is not null then 1 else 0 end) +
           (case when file_hash is not null then 1 else 0 end) +
           (case when unused                then 1 else 0 end) > 1 then
            sync_error.raise(sync_error.multiple_filters);
        end if;

        if release is not null then
            open repos for
                select repo_uuid,
                       release,
                       build,
                       file_path
                from repo
                where release = list_repos.release
                order by repo_uuid;
        elsif build is not null then
            open repos for
                select repo_uuid,
                       release,
                       build,
                       file_path
                from repo
                where build = list_repos.build
                order by repo_uuid;
        elsif file_path is not null then
            open repos for
                select repo_uuid,
                       release,
                       build,
                       file_path
                from repo
                where file_path = list_repos.file_path
                order by repo_uuid;
        elsif file_hash is not null then
            open repos for
                select distinct repo_uuid,
                                release,
                                build,
                                file_path
                from repo
                where file_hash = list_repos.file_hash
                order by repo_uuid;
        elsif unused then
            open repos for
                select repo_uuid,
                       release,
                       build,
                       file_path
                from repo
                where repo_uuid not in (select repo_uuid
                                        from device)
                order by repo_uuid;
        else
            open repos for
                select repo_uuid,
                       release,
                       build,
                       file_path
                from repo
                order by repo_uuid;
        end if;

        commit;

        return repos;
    exception
        when others then
            rollback;
            raise;
    end;

    function list_vms(
        vm_name     in varchar2,
        device_uuid in varchar2,
        disk_uuid   in varchar2,
        unused      in boolean
    ) return sys_refcursor is
        vms sys_refcursor;
    begin
        set transaction read only;

        sync_util.check_database_state;

        -- Check that no more than one filter is specified.
        if (case when vm_name     is not null then 1 else 0 end) +
           (case when device_uuid is not null then 1 else 0 end) +
           (case when disk_uuid   is not null then 1 else 0 end) +
           (case when unused                  then 1 else 0 end) > 1 then
            sync_error.raise(sync_error.multiple_filters);
        end if;

        if vm_name is not null then
            open vms for
                select vm_uuid,
                       vm_name
                from vm
                where vm_name = list_vms.vm_name
                order by vm_uuid;
        elsif device_uuid is not null then
            sync_util.check_device_exists(device_uuid);

            open vms for
                select distinct vm_uuid,
                                vm_name
                from vm
                     join vm_instance using (vm_uuid)
                where device_uuid = list_vms.device_uuid and
                      vm_instance.removed = sync_util.false_char
                order by vm_uuid;
        elsif disk_uuid is not null then
            check_disk_exists(disk_uuid);

            open vms for
                select vm_uuid,
                       vm_name
                from vm
                     join vm_disk using (vm_uuid)
                where disk_uuid = list_vms.disk_uuid
                order by vm_uuid;
        elsif unused then
            open vms for
                select vm_uuid,
                       vm_name
                from vm
                where vm_uuid not in (select vm_uuid
                                      from vm_instance
                                      where removed = sync_util.false_char)
                order by vm_uuid;
        else
            open vms for
                select vm_uuid,
                       vm_name
                from vm
                order by vm_uuid;
        end if;

        commit;

        return vms;
    exception
        when others then
            rollback;
            raise;
    end;

    function list_vms_ui(
        vm_name_contains in varchar2,
        config           in varchar2_list
    ) return sys_refcursor is
        pattern varchar2(2048);
        daemons varchar2_list;
        keys varchar2_list;
        vms sys_refcursor;
    begin
        set transaction read only;

        split_partial_config_list(config,
                                  2,
                                  daemons,
                                  keys);

        if vm_name_contains is not null then
            pattern := '%' ||
                       escape_like(lower(list_vms_ui.vm_name_contains)) || '%';
        end if;

        open vms for
            with vc1 as
                 (select vm_uuid,
                         value
                  from vm_config
                  where daemon = list_vms_ui.daemons(1) and
                        key = list_vms_ui.keys(1)),
                 vc2 as
                 (select vm_uuid,
                         value
                  from vm_config
                  where daemon = list_vms_ui.daemons(2) and
                        key = list_vms_ui.keys(2)),
                 vi as
                 (select vm_uuid,
                         count(*) num_vm_instances
                  from vm_instance
                  where removed = sync_util.false_char
                  group by vm_uuid)
            select vm_uuid,
                   vm_name,
                   vc1.value config_value_1,
                   vc2.value config_value_2,
                   nvl(vi.num_vm_instances, 0) num_vm_instances
            from vm
                 left outer join vc1 using (vm_uuid)
                 left outer join vc2 using (vm_uuid)
                 left outer join vi using (vm_uuid)
            where pattern is null or
                  lower(vm_name) like pattern escape '!'
            order by vm_uuid;

        commit;

        return vms;
    exception
        when others then
            rollback;
            raise;
    end;

    -- TODO: filter by locked?
    function list_vm_instances(
        vm_instance_name in varchar2,
        device_uuid      in varchar2,
        vm_uuid          in varchar2,
        disk_uuid        in varchar2,
        removed          in boolean
    ) return sys_refcursor is
        removed_char varchar2(1);
        vm_instances sys_refcursor;
    begin
        set transaction read only;

        sync_util.check_database_state;

        -- Check that no more than one filter is specified.
        if (case when vm_instance_name is not null then 1 else 0 end) +
           (case when device_uuid      is not null then 1 else 0 end) +
           (case when vm_uuid          is not null then 1 else 0 end) +
           (case when disk_uuid        is not null then 1 else 0 end) > 1 then
            sync_error.raise(sync_error.multiple_filters);
        end if;

        removed_char := boolean_to_char(removed);

        if vm_instance_name is not null then
            open vm_instances for
                select vm_instance_uuid,
                       device_uuid,
                       vm_uuid,
                       vm_instance_name,
                       locked
                from vm_instance
                where vm_instance_name = list_vm_instances.vm_instance_name and
                      removed = list_vm_instances.removed_char
                order by vm_instance_uuid;
        elsif device_uuid is not null then
            sync_util.check_device_exists(device_uuid);

            open vm_instances for
                select vm_instance_uuid,
                       device_uuid,
                       vm_uuid,
                       vm_instance_name,
                       locked
                from vm_instance
                where device_uuid = list_vm_instances.device_uuid and
                      removed = list_vm_instances.removed_char
                order by vm_instance_uuid;
        elsif vm_uuid is not null then
            check_vm_exists(vm_uuid);

            open vm_instances for
                select vm_instance_uuid,
                       device_uuid,
                       vm_uuid,
                       vm_instance_name,
                       locked
                from vm_instance
                where vm_uuid = list_vm_instances.vm_uuid and
                      removed = list_vm_instances.removed_char
                order by vm_instance_uuid;
        elsif disk_uuid is not null then
            check_disk_exists(disk_uuid);

            open vm_instances for
                select vm_instance_uuid,
                       device_uuid,
                       vm_uuid,
                       vm_instance_name,
                       locked
                from vm_instance
                     join vm_disk using (vm_uuid)
                where disk_uuid = list_vm_instances.disk_uuid and
                      removed = list_vm_instances.removed_char
                order by vm_instance_uuid;
        else
            open vm_instances for
                select vm_instance_uuid,
                       device_uuid,
                       vm_uuid,
                       vm_instance_name,
                       locked
                from vm_instance
                where removed = list_vm_instances.removed_char
                order by vm_instance_uuid;
        end if;

        commit;

        return vm_instances;
    exception
        when others then
            rollback;
            raise;
    end;

    function list_vm_insts_for_device_ui(
        device_uuid in varchar2,
        config      in varchar2_list
    ) return sys_refcursor is
        daemons varchar2_list;
        keys varchar2_list;
        vm_instances sys_refcursor;
    begin
        set transaction read only;

        sync_util.check_device_exists(device_uuid);

        split_partial_config_list(config,
                                  2,
                                  daemons,
                                  keys);

        open vm_instances for
            with vc1 as
                 (select vm_uuid,
                         value
                  from vm_config
                  where daemon = list_vm_insts_for_device_ui.daemons(1) and
                        key = list_vm_insts_for_device_ui.keys(1)),
                 vc2 as
                 (select vm_uuid,
                         value
                  from vm_config
                  where daemon = list_vm_insts_for_device_ui.daemons(2) and
                        key = list_vm_insts_for_device_ui.keys(2))
            select vm_instance_uuid,
                   vm_uuid,
                   vm_instance_name,
                   locked,
                   vc1.value config_value_1,
                   vc2.value config_value_2
            from vm_instance
                 left outer join vc1 using (vm_uuid)
                 left outer join vc2 using (vm_uuid)
            where device_uuid = list_vm_insts_for_device_ui.device_uuid and
                  vm_instance.removed = sync_util.false_char
            order by vm_instance_uuid;

        commit;

        return vm_instances;
    exception
        when others then
            rollback;
            raise;
    end;

    procedure lock_vm_instance(
        vm_instance_uuid in varchar2
    ) is
    begin
        sync_util.check_database_state;

        lock_unremoved_vm_instance_row(vm_instance_uuid);

        update vm_instance
        set locked = sync_util.true_char
        where vm_instance_uuid = lock_vm_instance.vm_instance_uuid and
              locked = sync_util.false_char;

        if sql%rowcount != 1 then
            sync_error.raise(sync_error.vm_inst_already_locked,
                             vm_instance_uuid);
        end if;

        commit;
    exception
        when others then
            rollback;
            raise;
    end;

    procedure modify_device_config(
        device_uuid in varchar2,
        config      in varchar2_list,
        replace     in boolean
    ) is
    begin
        sync_util.check_database_state;

        sync_util.lock_device_row(device_uuid);

        if replace then
            delete from device_config
            where device_uuid = modify_device_config.device_uuid;
        end if;

        insert_device_config(device_uuid, config);

        commit;
    exception
        when others then
            rollback;
            raise;
    end;

    procedure modify_device_repo(
        device_uuid in varchar2,
        repo_uuid   in varchar2
    ) is
    begin
        sync_util.check_database_state;

        begin
            update device
            set repo_uuid = modify_device_repo.repo_uuid
            where device_uuid = modify_device_repo.device_uuid;
        exception
            when sync_error.parent_key_not_found then
                case sync_error.get_violated_constraint
                    when 'device_fk1' then
                        sync_error.raise(sync_error.repo_not_found,
                                         repo_uuid);
                    else
                        raise;
                end case;

            when sync_error.value_too_large then
                case sync_error.get_violated_column
                    when 'device.repo_uuid' then
                        sync_error.raise(sync_error.repo_not_found,
                                         repo_uuid);
                    else
                        raise;
                end case;
        end;

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

    procedure purge_vm_instance(
        vm_instance_uuid in varchar2
    ) is
    begin
        sync_util.check_database_state;

        if vm_instance_uuid is null then
            sync_error.raise(sync_error.vm_inst_required);
        end if;

        delete from vm_instance
        where vm_instance_uuid = purge_vm_instance.vm_instance_uuid;

        if sql%rowcount != 1 then
            sync_error.raise(sync_error.vm_inst_not_found,
                             vm_instance_uuid);
        end if;

        commit;
    exception
        when others then
            rollback;
            raise;
    end;

    procedure readd_vm_instance(
        vm_instance_uuid in varchar2
    ) is
        device_uuid device.device_uuid%type;
    begin
        sync_util.check_database_state;

        lock_vm_instance_row(vm_instance_uuid);

        update vm_instance
        set removed = sync_util.false_char
        where vm_instance_uuid = readd_vm_instance.vm_instance_uuid and
              removed = sync_util.true_char;

        if sql%rowcount != 1 then
            sync_error.raise(sync_error.vm_inst_not_removed,
                             vm_instance_uuid);
        end if;

        commit;
    exception
        when others then
            rollback;
            raise;
    end;

    procedure remove_device(
        device_uuid in varchar2,
        cascade     in boolean
    ) is
    begin
        sync_util.check_database_state;

        sync_util.lock_device_row(device_uuid);

        if cascade then
            delete from vm_instance
            where device_uuid = remove_device.device_uuid;
        else
            delete from vm_instance
            where device_uuid = remove_device.device_uuid and
                  removed = sync_util.true_char;
        end if;

        delete from report_device
        where device_uuid = remove_device.device_uuid;

        delete from device_config
        where device_uuid = remove_device.device_uuid;

        begin
            delete from device
            where device_uuid = remove_device.device_uuid;
        exception
            when sync_error.child_record_found then
                case sync_error.get_violated_constraint
                    when 'vm_instance_fk1' then
                        sync_error.raise(sync_error.device_has_vm_inst,
                                         device_uuid);
                    else
                        raise;
                end case;
        end;

        update device_license
        set state = 'e'
        where device_uuid = remove_device.device_uuid and
              state = 'g';

        delete from device_license
        where device_uuid = remove_device.device_uuid and
              state = 'r';

        commit;
    exception
        when others then
            rollback;
            raise;
    end;

    procedure remove_disk(
        disk_uuid in varchar2
    ) is
    begin
        -- TODO: consider returning file_path so caller can remove the file?

        sync_util.check_database_state;

        if disk_uuid is null then
            sync_error.raise(sync_error.disk_required);
        end if;

        begin
            delete from disk
            where disk_uuid = remove_disk.disk_uuid;
        exception
            when sync_error.child_record_found then
                case sync_error.get_violated_constraint
                    when 'vm_disk_fk2' then
                        sync_error.raise(sync_error.disk_in_use,
                                         disk_uuid);
                    else
                        raise;
                end case;
        end;

        if sql%rowcount != 1 then
            sync_error.raise(sync_error.disk_not_found,
                             disk_uuid);
        end if;

        commit;
    exception
        when others then
            rollback;
            raise;
    end;

    procedure remove_repo(
        repo_uuid in varchar2
    ) is
    begin
        sync_util.check_database_state;

        if repo_uuid is null then
            sync_error.raise(sync_error.repo_required);
        end if;

        begin
            delete from repo
            where repo_uuid = remove_repo.repo_uuid;
        exception
            when sync_error.child_record_found then
                case sync_error.get_violated_constraint
                    when 'device_fk1' then
                        sync_error.raise(sync_error.repo_in_use,
                                         repo_uuid);
                    else
                        raise;
                end case;
        end;

        if sql%rowcount != 1 then
            sync_error.raise(sync_error.repo_not_found,
                             repo_uuid);
        end if;

        commit;
    exception
        when others then
            rollback;
            raise;
    end;

    procedure remove_vm(
        vm_uuid in varchar2,
        cascade in boolean
    ) is
    begin
        sync_util.check_database_state;

        lock_vm_row(vm_uuid);

        if cascade then
            delete from vm_instance
            where vm_uuid = remove_vm.vm_uuid;
        end if;

        delete from vm_disk
        where vm_uuid = remove_vm.vm_uuid;

        delete from vm_config
        where vm_uuid = remove_vm.vm_uuid;

        begin
            delete from vm
            where vm_uuid = remove_vm.vm_uuid;
        exception
            when sync_error.child_record_found then
                case sync_error.get_violated_constraint
                    when 'vm_instance_fk2' then
                        sync_error.raise(sync_error.vm_in_use,
                                         vm_uuid);
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

    procedure remove_vm_instance(
        vm_instance_uuid in varchar2
    ) is
    begin
        sync_util.check_database_state;

        lock_vm_instance_row(vm_instance_uuid);

        update vm_instance
        set removed = sync_util.true_char
        where vm_instance_uuid = remove_vm_instance.vm_instance_uuid and
              removed = sync_util.false_char;

        if sql%rowcount != 1 then
            sync_error.raise(sync_error.vm_inst_already_removed,
                             vm_instance_uuid);
        end if;

        commit;
    exception
        when others then
            rollback;
            raise;
    end;

    procedure reset_device_secret(
        device_uuid in varchar2
    ) is
        shared_secret device.shared_secret%type;
    begin
        sync_util.check_database_state;

        if device_uuid is null then
            sync_error.raise(sync_error.device_required);
        end if;

        shared_secret := generate_secret;

        update device
        set shared_secret = reset_device_secret.shared_secret
        where device_uuid = reset_device_secret.device_uuid;

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

    procedure unlock_vm_instance(
        vm_instance_uuid in varchar2
    ) is
    begin
        sync_util.check_database_state;

        lock_unremoved_vm_instance_row(vm_instance_uuid);

        update vm_instance
        set locked = sync_util.false_char
        where vm_instance_uuid = unlock_vm_instance.vm_instance_uuid and
              locked = sync_util.true_char;

        if sql%rowcount != 1 then
            sync_error.raise(sync_error.vm_inst_already_unlocked,
                             vm_instance_uuid);
        end if;

        commit;
    exception
        when others then
            rollback;
            raise;
    end;

    procedure verify_database is
    begin
        -- In previous versions of the schema, there were a few constraints
        -- on the data which couldn't be expressed as standard database
        -- constraints, and so were enforced only by the stored procedures.
        -- This procedure used to check that the data was consistent with
        -- those constraints.
        --
        -- This procedure no longer has a useful purpose, but has been kept
        -- for backwards compatibility and to allow similar constraints to be
        -- added in the future.

        set transaction read only;

        sync_util.check_database_state;

        commit;
    exception
        when others then
            rollback;
            raise;
    end;
end;
/
