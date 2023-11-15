    def _populate_from_source(self, source_data, using_current_cache):
        """
        Populate inventory data from direct source

        """
        if using_current_cache:
            self._populate_from_cache(source_data)
            return source_data

        cacheable_results = {}
        hostvars = {}
        objects = self._get_managed_objects_properties(vim_type=vim.VirtualMachine, properties=['name'])

        if self.with_tags:
            tag_svc = Tag(self.rest_content)
            tag_association = TagAssociation(self.rest_content)

            tags_info = dict()
            tags = tag_svc.list()
            for tag in tags:
                tag_obj = tag_svc.get(tag)
                tags_info[tag_obj.id] = tag_obj.name
                if tag_obj.name not in cacheable_results:
                    cacheable_results[tag_obj.name] = {'hosts': []}
                    self.inventory.add_group(tag_obj.name)

        for temp_vm_object in objects:
            for temp_vm_object_property in temp_vm_object.propSet:
                # VMware does not provide a way to uniquely identify VM by its name
                # i.e. there can be two virtual machines with same name
                # Appending "_" and VMware UUID to make it unique
                current_host = temp_vm_object_property.val + "_" + temp_vm_object.obj.config.uuid

                if current_host not in hostvars:
                    hostvars[current_host] = {}
                    self.inventory.add_host(current_host)
                    host_ip = temp_vm_object.obj.guest.ipAddress
                    if host_ip:
                        self.inventory.set_variable(current_host, 'ansible_host', host_ip)

                    # Load VM properties in host_vars
                    vm_properties = [
                        'name',
                        'config.cpuHotAddEnabled',
                        'config.cpuHotRemoveEnabled',
                        'config.instanceUuid',
                        'config.hardware.numCPU',
                        'config.template',
                        'config.name',
                        'guest.hostName',
                        'guest.ipAddress',
                        'guest.guestId',
                        'guest.guestState',
                        'runtime.maxMemoryUsage',
                        'customValue',
                    ]
                    for vm_prop in vm_properties:
                        vm_value = self._get_vm_prop(temp_vm_object.obj, vm_prop.split("."))
                        self.inventory.set_variable(current_host, vm_prop, vm_value)
                    # Only gather facts related to tag if vCloud and vSphere is installed.
                    if HAS_VCLOUD and HAS_VSPHERE and self.with_tags:
                        # Add virtual machine to appropriate tag group
                        vm_mo_id = temp_vm_object.obj._GetMoId()
                        vm_dynamic_id = DynamicID(type='VirtualMachine', id=vm_mo_id)
                        attached_tags = tag_association.list_attached_tags(vm_dynamic_id)

                        for tag_id in attached_tags:
                            self.inventory.add_child(tags_info[tag_id], current_host)
                            cacheable_results[tags_info[tag_id]]['hosts'].append(current_host)

                    # Based on power state of virtual machine
                    vm_power = temp_vm_object.obj.summary.runtime.powerState
                    if vm_power not in cacheable_results:
                        cacheable_results[vm_power] = []
                        self.inventory.add_group(vm_power)
                    cacheable_results[vm_power].append(current_host)
                    self.inventory.add_child(vm_power, current_host)

                    # Based on guest id
                    vm_guest_id = temp_vm_object.obj.config.guestId
                    if vm_guest_id and vm_guest_id not in cacheable_results:
                        cacheable_results[vm_guest_id] = []
                        self.inventory.add_group(vm_guest_id)
                    cacheable_results[vm_guest_id].append(current_host)
                    self.inventory.add_child(vm_guest_id, current_host)

        return cacheable_results