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

create synonym device         for &&sync_owner_user..device;
create synonym device_config  for &&sync_owner_user..device_config;
create synonym device_license for &&sync_owner_user..device_license;
create synonym disk           for &&sync_owner_user..disk;
create synonym repo           for &&sync_owner_user..repo;
create synonym report_device  for &&sync_owner_user..report_device;
create synonym synchronizer   for &&sync_owner_user..synchronizer;
create synonym version        for &&sync_owner_user..version;
create synonym vm             for &&sync_owner_user..vm;
create synonym vm_config      for &&sync_owner_user..vm_config;
create synonym vm_disk        for &&sync_owner_user..vm_disk;
create synonym vm_instance    for &&sync_owner_user..vm_instance;

create synonym sync_version for &&sync_owner_user..sync_version;
