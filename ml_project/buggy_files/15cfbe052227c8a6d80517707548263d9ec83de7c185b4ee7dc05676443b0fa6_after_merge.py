    def __hash__(self):
        var = self._get_identical_source(self)
        return hash((self.name, var.name, type(self), var._compute_value))