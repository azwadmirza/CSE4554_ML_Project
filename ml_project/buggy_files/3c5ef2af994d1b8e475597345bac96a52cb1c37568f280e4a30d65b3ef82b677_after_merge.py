    def check_output_duplicates(self):
        """Check ``Namedlist`` for duplicate entries and raise a ``WorkflowError``
        on problems.
        """
        seen = dict()
        idx = None
        for name, value in self.output._allitems():
            if name is None:
                if idx is None:
                    idx = 0
                else:
                    idx += 1
            if value in seen:
                raise WorkflowError(
                    "Duplicate output file pattern in rule {}. First two "
                    "duplicate for entries {} and {}".format(
                        self.name, seen[value], name or idx
                    )
                )
            seen[value] = name or idx