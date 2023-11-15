    def expand_output(self, wildcards):
        output = OutputFiles(o.apply_wildcards(wildcards) for o in self.output)
        output.take_names(self.output.get_names())
        mapping = {f: f_ for f, f_ in zip(output, self.output)}

        for f in output:
            f.check()

        # Note that we do not need to check for duplicate file names after
        # expansion as all output patterns have contain all wildcards anyway.

        return output, mapping