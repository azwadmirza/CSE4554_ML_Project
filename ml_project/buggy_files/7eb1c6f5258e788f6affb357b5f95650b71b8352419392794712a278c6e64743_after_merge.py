    def initializables(self):
        if self._externally_defined:
            return None
        return [(self.parameter_tensor, self.is_initialized_tensor)]