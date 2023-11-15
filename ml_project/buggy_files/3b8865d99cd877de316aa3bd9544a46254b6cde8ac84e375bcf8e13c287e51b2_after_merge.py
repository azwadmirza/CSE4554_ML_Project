    def get_variables(self):
        return FrozenOrderedDict((k, self.open_store_variable(self.ds[k]))
                                 for k in self.ds.keys())