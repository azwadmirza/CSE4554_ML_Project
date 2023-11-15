    def _add_host(self, vars):

        host_name = self._to_safe(vars['name'])
        resource_group = self._to_safe(vars['resource_group'])
        security_group = None
        if vars.get('security_group'):
            security_group = self._to_safe(vars['security_group'])

        if self.group_by_resource_group:
            if not self._inventory.get(resource_group):
                self._inventory[resource_group] = []
            self._inventory[resource_group].append(host_name)

        if self.group_by_location:
            if not self._inventory.get(vars['location']):
                self._inventory[vars['location']] = []
            self._inventory[vars['location']].append(host_name)

        if self.group_by_security_group and security_group:
            if not self._inventory.get(security_group):
                self._inventory[security_group] = []
            self._inventory[security_group].append(host_name)

        self._inventory['_meta']['hostvars'][host_name] = vars
        self._inventory['azure'].append(host_name)

        if self.group_by_tag and vars.get('tags'):
            for key, value in vars['tags'].items():
                safe_key = self._to_safe(key)
                safe_value = safe_key + '_' + self._to_safe(value)
                if not self._inventory.get(safe_key):
                    self._inventory[safe_key] = []
                if not self._inventory.get(safe_value):
                    self._inventory[safe_value] = []
                self._inventory[safe_key].append(host_name)
                self._inventory[safe_value].append(host_name)