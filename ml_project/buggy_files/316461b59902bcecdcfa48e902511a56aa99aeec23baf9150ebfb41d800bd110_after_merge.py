    def run(self):
        self.status = 'running'

        self._memory_results = {}
        for _ in range(self.program.num_shots):
            self.wf_simulator.reset()
            self._execute_program()
            for name in self.ram.keys():
                self._memory_results.setdefault(name, list())
                self._memory_results[name].append(self.ram[name])

        # TODO: this will need to be removed in merge conflict with #873
        self._bitstrings = self._memory_results['ro']

        return self