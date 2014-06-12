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

create or replace package sync_error as
    -- Oracle exceptions

    cannot_insert_null        exception;
    cannot_update_null        exception;
    precision_exceeded        exception;
    check_constraint_violated exception;
    parent_key_not_found      exception;
    child_record_found        exception;
    value_too_large           exception;

    pragma exception_init(cannot_insert_null,         -1400);
    pragma exception_init(cannot_update_null,         -1407);
    pragma exception_init(precision_exceeded,         -1438);
    pragma exception_init(check_constraint_violated,  -2290);
    pragma exception_init(parent_key_not_found,       -2291);
    pragma exception_init(child_record_found,         -2292);
    pragma exception_init(value_too_large,           -12899);

    -- Synchroniser errors

    auth_token_required         constant number := -20000;
    auth_token_too_long         constant number := -20001;
    device_name_required        constant number := -20002;
    device_name_too_long        constant number := -20003;
    device_not_found            constant number := -20004;
    device_required             constant number := -20005;
    disk_name_required          constant number := -20006;
    disk_name_too_long          constant number := -20007;
    disk_not_found              constant number := -20008;
    disk_repeated               constant number := -20009;
    disk_required               constant number := -20010;
    encryption_key_invalid      constant number := -20011;
    file_hash_invalid           constant number := -20013;
    file_hash_required          constant number := -20014;
    file_path_not_unique        constant number := -20015;
    file_path_required          constant number := -20016;
    file_path_too_long          constant number := -20017;
    file_size_invalid           constant number := -20018;
    file_size_required          constant number := -20019;
    multiple_filters            constant number := -20020;
    vm_inst_exists              constant number := -20029;
    vm_inst_name_required       constant number := -20030;
    vm_inst_name_too_long       constant number := -20031;
    vm_inst_not_found           constant number := -20032;
    vm_inst_required            constant number := -20033;
    vm_name_required            constant number := -20034;
    vm_name_too_long            constant number := -20035;
    vm_not_found                constant number := -20036;
    vm_required                 constant number := -20037;
    config_empty                constant number := -20038;
    config_invalid              constant number := -20039;
    config_daemon_too_long      constant number := -20040;
    config_key_too_long         constant number := -20041;
    config_value_too_long       constant number := -20042;
    vm_in_use                   constant number := -20043;
    disk_in_use                 constant number := -20044;
    device_has_vm_inst          constant number := -20047;
    vm_inst_already_locked      constant number := -20048;
    vm_inst_already_unlocked    constant number := -20049;
    vm_inst_already_removed     constant number := -20056;
    vm_inst_not_removed         constant number := -20057;
    vm_inst_removed             constant number := -20058;
    removed_vm_inst_exists      constant number := -20060;
    build_required              constant number := -20061;
    build_too_long              constant number := -20062;
    release_required            constant number := -20063;
    release_too_long            constant number := -20064;
    repo_exists                 constant number := -20065;
    repo_in_use                 constant number := -20071;
    repo_not_found              constant number := -20072;
    repo_required               constant number := -20073;
    expired_license_not_found   constant number := -20074;
    requested_license_not_found constant number := -20075;
    installation_incomplete     constant number := -20076;
    upgrade_incomplete          constant number := -20077;
    db_state_invalid            constant number := -20078;
    db_version_incompatible     constant number := -20079;
    disk_type_invalid           constant number := -20080;
    iso_with_encryption_key     constant number := -20081;
    iso_not_read_only           constant number := -20082;
    disk_read_only_and_shared   constant number := -20083;
    too_many_config_items       constant number := -20085;
    num_licenses_invalid        constant number := -20086;
    offline_licensing           constant number := -20087;
    out_of_licenses             constant number := -20088;

    -- When adding a new error, remember to update sync_db/error.py as well!

    procedure raise(
        error_code in number,
        param1     in varchar2 := null,
        param2     in varchar2 := null,
        param3     in varchar2 := null,
        param4     in varchar2 := null
    );

    function get_violated_column return varchar2;

    function get_violated_constraint return varchar2;
end;
/
