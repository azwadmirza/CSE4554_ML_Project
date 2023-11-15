    def get_item(self):
        self.log('Get properties for {0}'.format(self.name))
        item = None
        result = []

        try:
            item = self.compute_client.virtual_machines.get(self.resource_group, self.name)
        except CloudError as err:
            self.module.warn("Error getting virtual machine {0} - {1}".format(self.name, str(err)))

        if item and self.has_tags(item.tags, self.tags):
            result = [self.serialize_vm(item)]

        return result