    def validate(self):
        if not self.initialized:
            self.filters.extend(self.convert_deprecated())
            self.filters = self.filter_registry.parse(self.filters, self)
            self.initialized = True