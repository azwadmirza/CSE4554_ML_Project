    def create_inventory_file(self):
        """
        Creates the inventory file used by molecule, and returns None.

        :return: None
        """

        inventory = ''
        for instance in self.driver.instances:
            inventory += self.driver.inventory_entry(instance)

        groups = {}
        for instance in self.driver.instances:
            ansible_groups = instance.get('ansible_groups')
            if ansible_groups:
                for group in ansible_groups:
                    if isinstance(group, str):
                        if group not in groups:
                            groups[group] = []
                        groups[group].append(instance['name'])
                    elif isinstance(group, dict):
                        for group_name, group_list in group.iteritems():
                            for g in group_list:
                                if group_name not in groups:
                                    groups[group_name] = []
                                groups[group_name].append(g)

        if self.args.get('platform') == 'all':
            self.driver.platform = 'all'

        for group, subgroups in groups.iteritems():
            inventory += '\n[{}]\n'.format(group)
            for subgroup in subgroups:
                instance_name = util.format_instance_name(
                    subgroup, self.driver.platform, self.driver.instances)
                if instance_name:
                    inventory += '{}\n'.format(instance_name)
                else:
                    inventory += '{}\n'.format(subgroup)

        inventory_file = self.config.config['ansible']['inventory_file']
        try:
            util.write_file(inventory_file, inventory)
        except IOError:
            LOG.warning('WARNING: could not write inventory file {}'.format(
                inventory_file))