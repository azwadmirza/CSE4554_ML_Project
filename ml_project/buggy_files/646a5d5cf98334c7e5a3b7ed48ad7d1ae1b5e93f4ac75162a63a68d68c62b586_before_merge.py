    def check_argument_kinds(self, funckinds: List[int], sigkinds: List[int],
                             line: int) -> None:
        """Check that * and ** arguments are consistent.

        Arguments:
          funckinds: kinds of arguments in function definition
          sigkinds:  kinds of arguments in signature (after # type:)
        """
        for kind, token in [(nodes.ARG_STAR, '*'),
                            (nodes.ARG_STAR2, '**')]:
            if ((funckinds.count(kind) != sigkinds.count(kind)) or
                    (kind in funckinds and sigkinds.index(kind) != funckinds.index(kind))):
                self.fail(
                    "Inconsistent use of '{}' in function "
                    "signature".format(token), line)