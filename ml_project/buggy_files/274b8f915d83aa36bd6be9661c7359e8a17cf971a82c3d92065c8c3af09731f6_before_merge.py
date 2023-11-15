    def crawl(
        self,
        segment,
        dialect,
        parent_stack=None,
        siblings_pre=None,
        siblings_post=None,
        raw_stack=None,
        fix=False,
        memory=None,
    ):
        """Recursively perform the crawl operation on a given segment.

        Returns:
            A tuple of (vs, raw_stack, fixes, memory)

        """
        # parent stack should be a tuple if it exists

        # crawlers, should evaluate on segments FIRST, before evaluating on their
        # children. They should also return a list of violations.

        parent_stack = parent_stack or ()
        raw_stack = raw_stack or ()
        siblings_post = siblings_post or ()
        siblings_pre = siblings_pre or ()
        memory = memory or {}
        vs = []
        fixes = []

        # First, check whether we're looking at an unparsable and whether
        # this rule will still operate on that.
        if not self._works_on_unparsable and segment.is_type("unparsable"):
            # Abort here if it doesn't. Otherwise we'll get odd results.
            return vs, raw_stack, [], memory

        # TODO: Document what options are available to the evaluation function.
        try:
            res = self._eval(
                segment=segment,
                parent_stack=parent_stack,
                siblings_pre=siblings_pre,
                siblings_post=siblings_post,
                raw_stack=raw_stack,
                memory=memory,
                dialect=dialect,
            )
        # Any exception at this point would halt the linter and
        # cause the user to get no results
        except Exception as e:
            self.logger.critical(
                f"Applying rule {self.code} threw an Exception: {e}", exc_info=True
            )
            vs.append(
                SQLLintError(
                    rule=self,
                    segment=segment,
                    fixes=[],
                    description=(
                        f"""Unexpected exception: {str(e)};
                        Could you open an issue at https://github.com/sqlfluff/sqlfluff/issues ?
                        You can ignore this exception for now, by adding '--noqa: {self.code}' at the end
                        of line {segment.pos_marker.line_no}
                        """
                    ),
                )
            )
            return vs, raw_stack, fixes, memory

        if res is None:
            # Assume this means no problems (also means no memory)
            pass
        elif isinstance(res, LintResult):
            # Extract any memory
            memory = res.memory
            lerr = res.to_linting_error(rule=self)
            if lerr:
                vs.append(lerr)
            fixes += res.fixes
        elif isinstance(res, list) and all(
            isinstance(elem, LintResult) for elem in res
        ):
            # Extract any memory from the *last* one, assuming
            # it was the last to be added
            memory = res[-1].memory
            for elem in res:
                lerr = elem.to_linting_error(rule=self)
                if lerr:
                    vs.append(lerr)
                fixes += elem.fixes
        else:
            raise TypeError(
                "Got unexpected result [{0!r}] back from linting rule: {1!r}".format(
                    res, self.code
                )
            )

        # The raw stack only keeps track of the previous raw segments
        if len(segment.segments) == 0:
            raw_stack += (segment,)
        # Parent stack keeps track of all the parent segments
        parent_stack += (segment,)

        for idx, child in enumerate(segment.segments):
            dvs, raw_stack, child_fixes, memory = self.crawl(
                segment=child,
                parent_stack=parent_stack,
                siblings_pre=segment.segments[:idx],
                siblings_post=segment.segments[idx + 1 :],
                raw_stack=raw_stack,
                fix=fix,
                memory=memory,
                dialect=dialect,
            )
            vs += dvs
            fixes += child_fixes
        return vs, raw_stack, fixes, memory