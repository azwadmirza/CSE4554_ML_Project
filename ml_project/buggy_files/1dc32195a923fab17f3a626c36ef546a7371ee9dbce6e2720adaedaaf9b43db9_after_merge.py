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
                    # Only certain actions are support in to use in this case. Those actions are the
                    # "Global" salt-cloud actions defined in the "matching_states" dictionary above.
                    # If a more specific action is passed in, we shouldn't stack-trace - exit gracefully.
                    try:
                        state_action = matching_states[action]
                    except KeyError:
                        log.error(
                            'The use of \'{0}\' as an action is not supported in this context. '
                            'Only \'start\', \'stop\', and \'reboot\' are supported options.'.format(action)
                        )
                        raise SaltCloudException()
                    if (vm_details != 'Absent') and (vm_details['state'].lower() in state_action):
                        vm_names.append(vm_name)
        return vm_names