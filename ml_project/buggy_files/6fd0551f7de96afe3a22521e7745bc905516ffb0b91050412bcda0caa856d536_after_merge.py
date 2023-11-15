    def refine(self, typeinfer, target_type):
        # Do not back-propagate to locked variables (e.g. constants)
        assert target_type.is_precise()
        typeinfer.add_type(self.src, target_type, unless_locked=True,
                           loc=self.loc)