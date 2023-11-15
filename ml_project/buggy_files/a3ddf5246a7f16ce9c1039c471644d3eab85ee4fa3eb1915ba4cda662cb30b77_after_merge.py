    def persist_tree(self, verbosity=0):
        """Persist changes to the given path.

        We use the file_mask to do a safe merge, avoiding any templated
        sections. First we need to detect where there have been changes
        between the fixed and templated versions.

        We use difflib.SequenceMatcher.get_opcodes
        See: https://docs.python.org/3.7/library/difflib.html#difflib.SequenceMatcher.get_opcodes
        It returns a list of tuples ('equal|replace', ia1, ia2, ib1, ib2).

        """
        write_buff, success = self.fix_string(verbosity=verbosity)

        if success:
            # Actually write the file.
            with open(self.path, 'w') as f:
                f.write(write_buff)

        # TODO: Make return value of persist_changes() a more interesting result and then format it
        # click.echo(format_linting_fixes(result, verbose=verbose), color=color)
        return success