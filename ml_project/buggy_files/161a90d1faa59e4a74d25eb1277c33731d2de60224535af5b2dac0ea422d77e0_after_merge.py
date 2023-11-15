    def options(self):
        "Access of the options keywords when no cycles are defined."
        if not self.cyclic:
            return self[0]
        else:
            raise Exception("The options property may only be used"
                            " with non-cyclic Options.")