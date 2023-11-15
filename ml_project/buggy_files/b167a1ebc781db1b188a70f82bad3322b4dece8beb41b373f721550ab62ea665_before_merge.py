    def parse(self):
        if not self.raw:
            return

        self.update({'conda': []})

        for line in self.raw:
            if type(line) is dict:
                self.update(line)
            else:
                self['conda'].append(common.arg2spec(line))