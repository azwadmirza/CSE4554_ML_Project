    def _add_group(self, host, result_item):
        '''
        Helper function to add a group (if it does not exist), and to assign the
        specified host to that group.
        '''

        changed = False

        # the host here is from the executor side, which means it was a
        # serialized/cloned copy and we'll need to look up the proper
        # host object from the master inventory
        real_host = self._inventory.hosts.get(host.name)
        if real_host is None:
            if host.name == self._inventory.localhost.name:
                real_host = self._inventory.localhost
            else:
                raise AnsibleError('%s cannot be matched in inventory' % host.name)
        group_name = result_item.get('add_group')
        parent_group_names = result_item.get('parent_groups', [])

        for name in [group_name] + parent_group_names:
            if name not in self._inventory.groups:
                # create the new group and add it to inventory
                self._inventory.add_group(name)
                changed = True
        group = self._inventory.groups[group_name]
        for parent_group_name in parent_group_names:
            parent_group = self._inventory.groups[parent_group_name]
            parent_group.add_child_group(group)

        if real_host.name not in group.get_hosts():
            group.add_host(real_host)
            changed = True

        if group_name not in host.get_groups():
            real_host.add_group(group)
            changed = True

        if changed:
            self._inventory.reconcile_inventory()

        return changed