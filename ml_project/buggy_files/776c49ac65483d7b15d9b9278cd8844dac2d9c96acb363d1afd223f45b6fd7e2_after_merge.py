    def parse(self):
        if not self.raw:
            return

        self.update({'conda': []})

        for line in self.raw:
            if isinstance(line, dict):
                self.update(line)
            else:
                self['conda'].append(common.arg2spec(line))

        if 'pip' in self:
            if not self['pip']:
                del self['pip']
            if not any(MatchSpec(s).name == 'pip' for s in self['conda']):
                self['conda'].append('pip')