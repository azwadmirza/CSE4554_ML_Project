    def find(self, module_name):
        for finder in self.finders:
            section = finder.find(module_name)
            if section is not None:
                return section