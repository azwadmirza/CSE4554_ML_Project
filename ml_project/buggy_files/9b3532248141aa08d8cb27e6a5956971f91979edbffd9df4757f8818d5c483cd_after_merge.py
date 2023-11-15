        def cpu_affinity(self, cpus=None):
            """Get or set process CPU affinity.
            If specified 'cpus' must be a list of CPUs for which you
            want to set the affinity (e.g. [0, 1]).
            (Windows, Linux and BSD only).
            """
            if cpus is None:
                return self._proc.cpu_affinity_get()
            else:
                self._proc.cpu_affinity_set(cpus)