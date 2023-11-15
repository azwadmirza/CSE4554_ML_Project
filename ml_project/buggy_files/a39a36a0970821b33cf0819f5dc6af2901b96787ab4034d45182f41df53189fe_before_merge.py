    def _analyze_inst(self, inst):
        if isinstance(inst, ir.Assign):
            return self._analyze_assign(inst)
        return []