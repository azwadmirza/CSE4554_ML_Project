    def _populate_host_properties(self, vm_obj, current_host):
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
        field_mgr = self.pyv.content.customFieldsManager.field

        for vm_prop in vm_properties:
            if vm_prop == 'customValue':
                for cust_value in vm_obj.obj.customValue:
                    self.inventory.set_variable(current_host,
                                                [y.name for y in field_mgr if y.key == cust_value.key][0],
                                                cust_value.value)
            else:
                vm_value = self.pyv._get_object_prop(vm_obj.obj, vm_prop.split("."))
                self.inventory.set_variable(current_host, vm_prop, vm_value)