    def run(self):
        """
        Run a pyquil program on the QPU.

        This formats the classified data from the QPU server by stacking measured bits into
        an array of shape (trials, classical_addresses). The mapping of qubit to
        classical address is backed out from MEASURE instructions in the program, so
        only do measurements where there is a 1-to-1 mapping between qubits and classical
        addresses.

        :return: The QPU object itself.
        """
        super().run()

        request = QPURequest(program=self._executable.program,
                             patch_values=self._build_patch_values(),
                             id=str(uuid.uuid4()))

        job_id = self.client.call('execute_qpu_request', request=request, user=self.user)
        results = self._get_buffers(job_id)
        ro_sources = self._executable.ro_sources

        if results:
            bitstrings = _extract_bitstrings(ro_sources, results)
        else:
            bitstrings = None

        self._bitstrings = bitstrings
        self._last_results = results
        return self