    def run(self):
        """
        Run a Quil program on the QVM multiple times and return the values stored in the
        classical registers designated by the classical_addresses parameter.

        :return: An array of bitstrings of shape ``(trials, len(classical_addresses))``
        """

        super().run()

        if isinstance(self._executable, PyQuilExecutableResponse):
            quil_program = _extract_program_from_pyquil_executable_response(self._executable)
        elif isinstance(self._executable, Program):
            quil_program = self._executable
        else:
            raise TypeError("quil_binary argument must be a PyQuilExecutableResponse or a Program."
                            "This error is typically triggered by forgetting to pass (nativized)"
                            "Quil to native_quil_to_executable or by using a compiler meant to be"
                            "used for jobs bound for a QPU.")

        trials = quil_program.num_shots
        classical_addresses = get_classical_addresses_from_program(quil_program)

        if self.noise_model is not None:
            quil_program = apply_noise_model(quil_program, self.noise_model)

        quil_program = self.augment_program_with_memory_values(quil_program)
        try:
            self._bitstrings = self.connection._qvm_run(quil_program=quil_program,
                                                        classical_addresses=classical_addresses,
                                                        trials=trials,
                                                        measurement_noise=self.measurement_noise,
                                                        gate_noise=self.gate_noise,
                                                        random_seed=self.random_seed)['ro']
        except KeyError:
            warnings.warn("You are running a QVM program with no MEASURE instructions. "
                          "The result of this program will always be an empty array. Are "
                          "you sure you didn't mean to measure some of your qubits?")
            self._bitstrings = np.zeros((trials, 0), dtype=np.int64)

        return self