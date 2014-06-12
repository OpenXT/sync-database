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

grant select on device         to &&sync_admin_user;
grant select on device_config  to &&sync_admin_user;
grant select on device_license to &&sync_admin_user;
grant select on disk           to &&sync_admin_user;
grant select on repo           to &&sync_admin_user;
grant select on report_device  to &&sync_admin_user;
grant select on synchronizer   to &&sync_admin_user;
grant select on version        to &&sync_admin_user;
grant select on vm             to &&sync_admin_user;
grant select on vm_config      to &&sync_admin_user;
grant select on vm_disk        to &&sync_admin_user;
grant select on vm_instance    to &&sync_admin_user;

grant execute on sync_admin    to &&sync_admin_user;
grant execute on sync_version  to &&sync_admin_user;

grant select on device         to &&sync_license_user;
grant select on device_config  to &&sync_license_user;
grant select on device_license to &&sync_license_user;
grant select on disk           to &&sync_license_user;
grant select on repo           to &&sync_license_user;
grant select on report_device  to &&sync_license_user;
grant select on synchronizer   to &&sync_license_user;
grant select on version        to &&sync_license_user;
grant select on vm             to &&sync_license_user;
grant select on vm_config      to &&sync_license_user;
grant select on vm_disk        to &&sync_license_user;
grant select on vm_instance    to &&sync_license_user;

grant execute on sync_license  to &&sync_license_user;
grant execute on sync_version  to &&sync_license_user;

grant select on device         to &&sync_server_user;
grant select on device_config  to &&sync_server_user;
grant select on device_license to &&sync_server_user;
grant select on disk           to &&sync_server_user;
grant select on repo           to &&sync_server_user;
grant select on report_device  to &&sync_server_user;
grant select on synchronizer   to &&sync_server_user;
grant select on version        to &&sync_server_user;
grant select on vm             to &&sync_server_user;
grant select on vm_config      to &&sync_server_user;
grant select on vm_disk        to &&sync_server_user;
grant select on vm_instance    to &&sync_server_user;

grant execute on sync_server   to &&sync_server_user;
grant execute on sync_version  to &&sync_server_user;
