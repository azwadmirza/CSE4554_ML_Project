    def output_mintime(self):
        """ Return oldest output file. """

        existing = [f.mtime for f in self.expanded_output if f.exists]
        if self.benchmark and self.benchmark.exists:
            existing.append(self.benchmark.mtime)
        if existing:
            return min(existing)
        return None