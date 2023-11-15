    def initializables(self):
        if self._externally_defined:
            return None
        return [self.parameter_tensor]