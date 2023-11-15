    def __hash__(self):
        var = self._get_identical_source(self)
        return hash((var.name, type(self), var._compute_value))