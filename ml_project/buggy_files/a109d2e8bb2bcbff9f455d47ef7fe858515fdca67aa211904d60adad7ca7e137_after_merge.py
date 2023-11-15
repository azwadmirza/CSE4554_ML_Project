    def output_mintime(self):
        """ Return oldest output file. """
        try:
            mintime = min(
                f.mtime.local_or_remote() for f in self.expanded_output if f.exists
            )
        except ValueError:
            # no existing output
            mintime = None

        if self.benchmark and self.benchmark.exists:
            mintime_benchmark = self.benchmark.mtime.local_or_remote()
            if mintime is not None:
                return min(mintime, mintime_benchmark)
            else:
                return mintime_benchmark

        return mintime