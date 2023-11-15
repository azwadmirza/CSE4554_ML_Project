    def _lint_references_and_aliases(self, aliases, references, using_cols, parent_select):
        """Check whether any aliases are duplicates.

        NB: Subclasses of this error should override this function.

        """
        # Are any of the aliases the same?
        for a1, a2 in itertools.combinations(aliases, 2):
            # Compare the strings
            if a1[0] == a2[0] and a1[0]:
                # If there are any, then the rest of the code
                # won't make sense so just return here.
                return [LintResult(
                    # Reference the element, not the string.
                    anchor=a2[1],
                    description=("Duplicate table alias {0!r}. Table "
                                 "aliases should be unique.").format(a2.raw)
                )]
        return None