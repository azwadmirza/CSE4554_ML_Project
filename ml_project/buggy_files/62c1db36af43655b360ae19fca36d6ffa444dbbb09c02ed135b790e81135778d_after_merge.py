    def load(self, executable):
        if isinstance(executable, PyQuilExecutableResponse):
            program = _extract_program_from_pyquil_executable_response(executable)
        else:
            program = executable

        # initialize program counter
        self.program = program
        self.program_counter = 0
        self._memory_results = None

        # clear RAM, although it's not strictly clear if this should happen here
        self.ram = {}
        # if we're clearing RAM, we ought to clear the WF too
        self.wf_simulator.reset()

        # grab the gate definitions for future use
        self._extract_defined_gates()

        self.status = 'loaded'
        return self