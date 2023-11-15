    def get_dependent_data_keys(self):
        return [dep.key for dep, has_dep
                in zip(self.inputs or (), self.prepare_inputs) if has_dep]