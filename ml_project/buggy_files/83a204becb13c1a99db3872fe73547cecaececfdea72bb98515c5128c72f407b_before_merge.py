    def get_dependent_data_keys(self):
        if self.stage == OperandStage.reduce:
            inputs = self.inputs or ()
            return [(chunk.key, self._shuffle_key)
                    for proxy in inputs for chunk in proxy.inputs or ()]
        return super().get_dependent_data_keys()