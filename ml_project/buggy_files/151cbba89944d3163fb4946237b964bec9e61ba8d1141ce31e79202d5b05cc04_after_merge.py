    def exec_module(self, **kwargs):

        for key in self.module_arg_spec:
            setattr(self, key, kwargs[key])

        if self.name and not self.resource_group:
            self.fail("Parameter error: resource group required when filtering by name.")
        if self.name:
            self.results['vms'] = self.get_item()
        elif self.resource_group:
            self.results['vms'] = self.list_items_by_resourcegroup()
        else:
            self.results['vms'] = self.list_all_items()

        return self.results