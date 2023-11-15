    def get_vmnames_by_action(self, action):
        query_map = self.interpolated_map("list_nodes")
        matching_states = {
            'start': ['stopped'],
            'stop': ['running', 'active'],
            'reboot': ['running', 'active'],
        }
        vm_names = []
        for alias, drivers in query_map.items():
            for driver, vms in drivers.items():
                for vm_name, vm_details in vms.items():
                    if (vm_details != 'Absent') and \
                        (
                            vm_details['state'].lower() in
                            matching_states[action]
                            ):
                        vm_names.append(vm_name)
        return vm_names