    def load(self, executable):
        """
        Initialize a QAM into a fresh state.

        :param executable: Load a compiled executable onto the QAM.
        """
        assert self.status in ['connected', 'done']

        self._variables_shim = {}
        self._executable = executable
        self._bitstrings = None
        self.status = 'loaded'
        return self