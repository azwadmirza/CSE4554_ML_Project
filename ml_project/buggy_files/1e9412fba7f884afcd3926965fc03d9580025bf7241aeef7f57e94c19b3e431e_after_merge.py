    def execute(self, program: Program):
        """
        Execute one outer loop of a program on the QVM.

        Note that the QAM is stateful. Subsequent calls to :py:func:`execute` will not
        automatically reset the wavefunction or the classical RAM. If this is desired,
        consider starting your program with ``RESET``.

        :return: ``self`` to support method chaining.
        """
        self.program = program
        self._extract_defined_gates()
        return self._execute_program()