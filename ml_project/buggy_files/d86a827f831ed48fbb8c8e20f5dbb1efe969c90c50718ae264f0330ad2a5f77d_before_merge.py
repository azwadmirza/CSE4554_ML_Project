    def _populate_from_cache(self, source_data):
        """
        Populate inventory from cache
        """
        hostvars = source_data.pop('_meta', {}).get('hostvars', {})
        for group in source_data:
            if group == 'all':
                continue
            else:
                self.inventory.add_group(group)
                self.inventory.add_child('all', group)
        if not source_data:
            for host in hostvars:
                self.inventory.add_host(host)