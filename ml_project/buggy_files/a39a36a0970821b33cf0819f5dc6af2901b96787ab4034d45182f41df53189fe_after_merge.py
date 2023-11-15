    def _analyze_inst(self, inst):
        if isinstance(inst, ir.Assign):
            return self._analyze_assign(inst)
        elif type(inst) in array_analysis_extensions:
            # let external calls handle stmt if type matches
            f = array_analysis_extensions[type(inst)]
            return f(inst, self)
        return []