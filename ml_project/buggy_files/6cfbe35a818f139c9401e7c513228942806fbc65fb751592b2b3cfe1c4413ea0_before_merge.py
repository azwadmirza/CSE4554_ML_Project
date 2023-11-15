    def populate(self):
        super(Hardware, self).populate()
        data = self.responses[0]
        if data:
            self.facts['filesystems'] = self.parse_filesystems(data)

        data = self.responses[1]
        if data:
            processor_line = [l for l in data.splitlines()
                              if 'Processor' in l].pop()
            match = re.findall(r'\s(\d+)\s', processor_line)
            if match:
                self.facts['memtotal_mb'] = int(match[0]) / 1024
                self.facts['memfree_mb'] = int(match[3]) / 1024