    def get_dependent_data_keys(self):
        if self.stage == OperandStage.reduce:
            inputs = self.inputs or ()
            deps = []
            for inp in inputs:
                if isinstance(inp.op, (ShuffleProxy, FetchShuffle)):
                    deps.extend([(chunk.key, self._shuffle_key) for chunk in inp.inputs or ()])
                else:
                    deps.append(inp.key)
            return deps
        return super().get_dependent_data_keys()