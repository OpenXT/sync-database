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

alter table device
    add constraint device_fk1
    foreign key (repo_uuid)
    references repo (repo_uuid)
    deferrable;

------------------------------------------------------------------------------
-- device_config
------------------------------------------------------------------------------

alter table device_config
    add constraint device_config_fk1
    foreign key (device_uuid)
    references device (device_uuid)
    deferrable;

------------------------------------------------------------------------------
-- report_device
------------------------------------------------------------------------------

alter table report_device
    add constraint report_device_fk1
    foreign key (device_uuid)
    references device (device_uuid)
    deferrable;

------------------------------------------------------------------------------
-- vm_config
------------------------------------------------------------------------------

alter table vm_config
    add constraint vm_config_fk1
    foreign key (vm_uuid)
    references vm (vm_uuid)
    deferrable;

------------------------------------------------------------------------------
-- vm_disk
------------------------------------------------------------------------------

alter table vm_disk
    add constraint vm_disk_fk1
    foreign key (vm_uuid)
    references vm (vm_uuid)
    deferrable;

alter table vm_disk
    add constraint vm_disk_fk2
    foreign key (disk_uuid)
    references disk (disk_uuid)
    deferrable;

------------------------------------------------------------------------------
-- vm_instance
------------------------------------------------------------------------------

alter table vm_instance
    add constraint vm_instance_fk1
    foreign key (device_uuid)
    references device (device_uuid)
    deferrable;

alter table vm_instance
    add constraint vm_instance_fk2
    foreign key (vm_uuid)
    references vm (vm_uuid)
    deferrable;
