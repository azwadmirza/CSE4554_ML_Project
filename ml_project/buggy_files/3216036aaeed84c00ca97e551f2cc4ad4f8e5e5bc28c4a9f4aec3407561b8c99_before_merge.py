    def parse_stacks(self, data):
        match = re.findall(r'^Model number\s+: (\S+)', data, re.M)
        if match:
            self.facts['stacked_models'] = match

        match = re.findall(r'^System serial number\s+: (\S+)', data, re.M)
        if match:
            self.facts['stacked_serialnums'] = match