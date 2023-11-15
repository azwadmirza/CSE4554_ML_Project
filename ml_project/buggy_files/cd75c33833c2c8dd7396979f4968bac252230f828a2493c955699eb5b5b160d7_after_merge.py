    def get_dependent_data_keys(self):
        return [dep.key for dep in self.inputs or ()]