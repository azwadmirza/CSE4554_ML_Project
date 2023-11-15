    def finalize(self):
        """
        Finalize the PassManager, after which no more passes may be added
        without re-finalization.
        """
        self._analysis = self.dependency_analysis()
        self._print_after = self._debug_init()
        self._finalized = True