    def augment(self, resources):
        return [r for r in resources if self.manager.resource_type.id in r]