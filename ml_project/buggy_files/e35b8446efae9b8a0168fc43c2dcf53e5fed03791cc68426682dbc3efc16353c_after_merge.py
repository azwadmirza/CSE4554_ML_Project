    def get_item(self):
        self.log('Get properties for {0}'.format(self.name))
        item = None
        result = []

        item = self.get_vm(self.resource_group, self.name)

        if item and self.has_tags(item.get('tags'), self.tags):
            result = [item]

        return result