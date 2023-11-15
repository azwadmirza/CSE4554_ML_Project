    def populate(self):
        data = self.run('dir')
        if data:
            self.facts['filesystems'] = self.parse_filesystems(data)

        data = None
        try:
            data = self.run('show system resources', output='json')
        except ConnectionError:
            data = self.run('show system resources')
        if data:
            if isinstance(data, dict):
                self.facts['memtotal_mb'] = int(data['memory_usage_total']) / 1024
                self.facts['memfree_mb'] = int(data['memory_usage_free']) / 1024
            else:
                self.facts['memtotal_mb'] = self.parse_memtotal_mb(data)
                self.facts['memfree_mb'] = self.parse_memfree_mb(data)