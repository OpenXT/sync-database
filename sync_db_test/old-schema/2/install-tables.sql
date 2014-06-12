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

------------------------------------------------------------------------------
-- device
------------------------------------------------------------------------------

create table device
(
    device_uuid         varchar2(36)                       not null,
    device_name         varchar2(200)                      not null, -- FIXME: size
    shared_secret       varchar2(32)                       not null, -- FIXME: size?
    repo_uuid           varchar2(36),
    license_expiry_time timestamp(0) with local time zone,
    license_hash        varchar2(64)
);

create index device_pk
    on device (device_uuid);

alter table device
    add constraint device_pk
    primary key (device_uuid)
    using index device_pk;

-- device_ak1 is needed for the foreign key to repo.
create index device_ak1
    on device (repo_uuid);

alter table device
    add constraint device_ck1
    check (lengthb(device_uuid) = 36 and
           translate(device_uuid, '_0123456789abcdef-', '_') is null);

alter table device
    add constraint device_ck2
    check (lengthb(shared_secret) = 32 and
           translate(shared_secret, '_0123456789abcdef', '_') is null);

alter table device
    add constraint device_ck3
    check ((license_expiry_time is not null and license_hash is not null) or
           (license_expiry_time is null and license_hash is null));

------------------------------------------------------------------------------
-- device_config
------------------------------------------------------------------------------

create table device_config
(
    device_uuid varchar2(36)   not null,
    daemon      varchar2(100)  not null, -- FIXME: size?
    key         varchar2(100)  not null, -- FIXME: size?
    value       varchar2(3500) not null  -- FIXME: size?
);

create index device_config_pk
    on device_config (device_uuid, daemon, key);

alter table device_config
    add constraint device_config_pk
    primary key (device_uuid, daemon, key)
    using index device_config_pk;

------------------------------------------------------------------------------
-- device_license
------------------------------------------------------------------------------

create table device_license
(
    device_uuid varchar2(36)  not null,
    state       varchar2(1)   not null
);

create index device_license_pk
    on device_license (device_uuid);

alter table device_license
    add constraint device_license_pk
    primary key (device_uuid)
    using index device_license_pk;

alter table device_license
    add constraint device_license_ck1
    check (lengthb(device_uuid) = 36 and
           translate(device_uuid, '_0123456789abcdef-', '_') is null);

-- r: requested
-- g: granted
-- e: expired
alter table device_license
    add constraint device_license_ck2
    check (state in ('r', 'g', 'e'));

------------------------------------------------------------------------------
-- device_user
------------------------------------------------------------------------------

create table device_user
(
    device_uuid varchar2(36) not null,
    user_uuid   varchar2(36) not null,
    removed     varchar2(1)  not null
);

create index device_user_pk
    on device_user (device_uuid, user_uuid);

alter table device_user
    add constraint device_user_pk
    primary key (device_uuid, user_uuid)
    using index device_user_pk;

-- device_user_ak1 is needed for the foreign key to user_.
create index device_user_ak1
    on device_user (user_uuid);

alter table device_user
    add constraint device_user_ck1
    check (removed in ('t', 'f'));

------------------------------------------------------------------------------
-- disk
------------------------------------------------------------------------------

create table disk
(
    disk_uuid      varchar2(36)   not null,
    disk_name      varchar2(200)  not null, -- FIXME: size?
    disk_type      varchar2(1)    not null,
    file_path      varchar2(1024) not null, -- FIXME: size?
        -- FIXME: assume this contains path relative to some root dir?
    file_size      number(13)     not null, -- FIXME: size?
    file_hash      varchar2(64)   not null, -- FIXME: size?
    encryption_key varchar2(128),
    shared         varchar2(1)    not null,
    read_only      varchar2(1)    not null
);

create index disk_pk
    on disk (disk_uuid);

alter table disk
    add constraint disk_pk
    primary key (disk_uuid)
    using index disk_pk;

create index disk_uk1
    on disk (file_path);

alter table disk
    add constraint disk_uk1
    unique (file_path)
    using index disk_uk1;

alter table disk
    add constraint disk_ck1
    check (lengthb(disk_uuid) = 36 and
           translate(disk_uuid, '_0123456789abcdef-', '_') is null);

alter table disk
    add constraint disk_ck2
    check (file_size >= 0);

alter table disk
    add constraint disk_ck3
    check (lengthb(file_hash) = 64 and
           translate(file_hash, '_0123456789abcdef', '_') is null);

alter table disk
    add constraint disk_ck4
    -- encrpytion_key is a hex string, so lengthb() = 128 is a 512 bit key.
    -- FIXME: we are arbitrarily requiring 256 or 512 bit keys here, with
    -- no justification, and no configuration control.
    check (lengthb(encryption_key) in (64, 128) and
           translate(encryption_key, '_0123456789abcdef', '_') is null);

alter table disk
    add constraint disk_ck5
    check (shared in ('t', 'f'));

-- i: iso
-- v: vhd
alter table disk
    add constraint disk_ck6
    check (disk_type in ('i', 'v'));

alter table disk
    add constraint disk_ck7
    check (not(disk_type = 'i' and encryption_key is not null));

alter table disk
    add constraint disk_ck8
    check (read_only in ('t', 'f'));

alter table disk
    add constraint disk_ck9
    check (not(disk_type = 'i' and read_only = 'f'));

alter table disk
    add constraint disk_ck10
    check (not(shared = 't' and read_only = 't'));

------------------------------------------------------------------------------
-- repo
------------------------------------------------------------------------------

create table repo
(
    repo_uuid varchar2(36)   not null,
    release   varchar2(100)  not null,
    build     varchar2(100)  not null,
    file_path varchar2(1024) not null, -- FIXME: size?
    file_size number(13)     not null, -- FIXME: size?
    file_hash varchar2(64)   not null  -- FIXME: size?
);

create index repo_pk
    on repo (repo_uuid);

alter table repo
    add constraint repo_pk
    primary key (repo_uuid)
    using index repo_pk;

create index repo_uk1
    on repo (file_path);

alter table repo
    add constraint repo_uk1
    unique (file_path)
    using index repo_uk1;

create index repo_uk2
    on repo (release, build);

alter table repo
    add constraint repo_uk2
    unique (release, build)
    using index repo_uk2;

alter table repo
    add constraint repo_ck1
    check (lengthb(repo_uuid) = 36 and
           translate(repo_uuid, '_0123456789abcdef-', '_') is null);

alter table repo
    add constraint repo_ck2
    check (file_size >= 0);

alter table repo
    add constraint repo_ck3
    check (lengthb(file_hash) = 64 and
           translate(file_hash, '_0123456789abcdef', '_') is null);

------------------------------------------------------------------------------
-- report_device
------------------------------------------------------------------------------

create table report_device
(
    device_uuid varchar2(36)                      not null,
    report_time timestamp(0) with local time zone not null,
    release     varchar2(100),
    build       varchar2(100)
);

create index report_device_pk
    on report_device (device_uuid);

alter table report_device
    add constraint report_device_pk
    primary key (device_uuid)
    using index report_device_pk;

------------------------------------------------------------------------------
-- user_
------------------------------------------------------------------------------

-- 'user' is a reserved word.

create table user_
(
    user_uuid  varchar2(36)   not null,
    user_name  varchar2(200)  not null, -- FIXME: size?
    auth_token varchar2(1024) not null, -- FIXME: type, size?
    removed    varchar2(1)    not null
);

create index user_pk
    on user_ (user_uuid);

alter table user_
    add constraint user_pk
    primary key (user_uuid)
    using index user_pk;

alter table user_
    add constraint user_ck1
    check (lengthb(user_uuid) = 36 and
           translate(user_uuid, '_0123456789abcdef-', '_') is null);

alter table user_
    add constraint user_ck2
    check (removed in ('t', 'f'));

-- FIXME: how does auth_token work? consider adding index
-- FIXME: is user_name unique? consider adding index
-- FIXME: is auth_token optional?

------------------------------------------------------------------------------
-- vm
------------------------------------------------------------------------------

create table vm
(
    vm_uuid varchar2(36)  not null,
    vm_name varchar2(200) not null  -- FIXME: size?
);

create index vm_pk
    on vm (vm_uuid);

alter table vm
    add constraint vm_pk
    primary key (vm_uuid)
    using index vm_pk;

alter table vm
    add constraint vm_ck1
    check (lengthb(vm_uuid) = 36 and
           translate(vm_uuid, '_0123456789abcdef-', '_') is null);

------------------------------------------------------------------------------
-- vm_config
------------------------------------------------------------------------------

create table vm_config
(
    vm_uuid varchar2(36)   not null,
    daemon  varchar2(100)  not null, -- FIXME: size?
    key     varchar2(100)  not null, -- FIXME: size?
    value   varchar2(3500) not null  -- FIXME: size?
);

create index vm_config_pk
    on vm_config (vm_uuid, daemon, key);

alter table vm_config
    add constraint vm_config_pk
    primary key (vm_uuid, daemon, key)
    using index vm_config_pk;

------------------------------------------------------------------------------
-- vm_disk
------------------------------------------------------------------------------

create table vm_disk
(
    vm_uuid     varchar2(36) not null,
    disk_uuid   varchar2(36) not null,
    disk_order  number(9)    not null  -- FIXME: size?
);

create index vm_disk_pk
    on vm_disk (vm_uuid, disk_uuid);

alter table vm_disk
    add constraint vm_disk_pk
    primary key (vm_uuid, disk_uuid)
    using index vm_disk_pk;

create index vm_disk_uk1
    on vm_disk (vm_uuid, disk_order);

alter table vm_disk
    add constraint vm_disk_uk1
    unique (vm_uuid, disk_order)
    using index vm_disk_uk1;

-- vm_disk_ak1 is needed for the foreign key to disk.
create index vm_disk_ak1
    on vm_disk (disk_uuid);

------------------------------------------------------------------------------
-- vm_instance
------------------------------------------------------------------------------

create table vm_instance
(
    vm_instance_uuid varchar2(36)  not null,
    device_uuid      varchar2(36)  not null,
    user_uuid        varchar2(36)  not null,
    vm_uuid          varchar2(36)  not null,
    vm_instance_name varchar2(200) not null, -- FIXME: size?
    locked           varchar2(1)   not null,
    removed          varchar2(1)   not null
);

create index vm_instance_pk
    on vm_instance (vm_instance_uuid);

alter table vm_instance
    add constraint vm_instance_pk
    primary key (vm_instance_uuid)
    using index vm_instance_pk;

create index vm_instance_uk1
    on vm_instance (device_uuid, user_uuid, vm_uuid);

alter table vm_instance
    add constraint vm_instance_uk1
    unique (device_uuid, user_uuid, vm_uuid)
    using index vm_instance_uk1;

-- vm_instance_ak1 is to allow efficient queries by user_uuid.
create index vm_instance_ak1
    on vm_instance (user_uuid);

-- vm_instance_ak2 is needed for the foreign key to vm.
create index vm_instance_ak2
    on vm_instance (vm_uuid);

alter table vm_instance
    add constraint vm_instance_ck1
    check (lengthb(vm_instance_uuid) = 36 and
           translate(vm_instance_uuid, '_0123456789abcdef-', '_') is null);

alter table vm_instance
    add constraint vm_instance_ck2
    check (locked in ('t', 'f'));

alter table vm_instance
    add constraint vm_instance_ck3
    check (removed in ('t', 'f'));
