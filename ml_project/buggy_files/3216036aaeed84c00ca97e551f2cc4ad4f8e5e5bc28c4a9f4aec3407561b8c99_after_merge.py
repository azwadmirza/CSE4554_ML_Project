    def parse_stacks(self, data):
        match = re.findall(r'^Model [Nn]umber\s+: (\S+)', data, re.M)
        if match:
            self.facts['stacked_models'] = match

        match = re.findall(r'^System [Ss]erial [Nn]umber\s+: (\S+)', data, re.M)
        if match:
            self.facts['stacked_serialnums'] = match