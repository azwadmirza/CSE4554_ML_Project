    def populate(self):
        data = self.run('dir')
        if data:
            self.facts['filesystems'] = self.parse_filesystems(data)

        data = self.run('show system resources', output='json')
        if data:
            self.facts['memtotal_mb'] = int(data['memory_usage_total']) / 1024
            self.facts['memfree_mb'] = int(data['memory_usage_free']) / 1024