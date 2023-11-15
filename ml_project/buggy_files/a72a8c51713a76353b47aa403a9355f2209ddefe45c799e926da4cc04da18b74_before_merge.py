    def validate(self):
        self.filters.extend(self.convert_deprecated())
        self.filters = self.filter_registry.parse(
            self.filters, self.policy.resource_manager)