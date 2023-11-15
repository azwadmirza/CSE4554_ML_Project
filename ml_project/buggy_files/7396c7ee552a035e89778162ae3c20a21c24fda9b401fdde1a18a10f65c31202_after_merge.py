    def _eval(self, segment, raw_stack, **kwargs):
        """Line is too long.

        This only triggers on newline segments, evaluating the whole line.
        The detection is simple, the fixing is much trickier.

        """
        if segment.name == 'newline':
            # iterate to buffer the whole line up to this point
            this_line = []
            idx = -1
            while True:
                if len(raw_stack) >= abs(idx):
                    s = raw_stack[idx]
                    if s.name == 'newline':
                        break
                    else:
                        this_line.insert(0, s)
                        idx -= 1
                else:
                    break

            # Now we can work out the line length and deal with the content
            line_len = sum(len(s.raw) for s in this_line)
            if line_len > self.max_line_length:
                # Problem, we'll be reporting a violation. The
                # question is, can we fix it?

                # We'll need the indent, so let's get it for fixing.
                line_indent = []
                idx = 0
                for s in this_line:
                    if s.name == 'whitespace':
                        line_indent.append(s)
                    else:
                        break

                # Does the line end in an inline comment that we can move back?
                if this_line[-1].name == 'inline_comment':
                    # Set up to delete the original comment and the preceeding whitespace
                    delete_buffer = [LintFix('delete', this_line[-1])]
                    idx = -2
                    while True:
                        if len(this_line) >= abs(idx) and this_line[idx].name == 'whitespace':
                            delete_buffer.append(LintFix('delete', this_line[idx]))
                            idx -= 1
                        else:
                            break
                    # Create a newline before this one with the existing comment, an
                    # identical indent AND a terminating newline, copied from the current
                    # target segment.
                    create_buffer = [
                        LintFix(
                            'create', this_line[0],
                            line_indent + [this_line[-1], segment]
                        )
                    ]
                    return LintResult(anchor=segment, fixes=delete_buffer + create_buffer)

                fixes = self._eval_line_for_breaks(this_line)
                if fixes:
                    return LintResult(anchor=segment, fixes=fixes)
                return LintResult(anchor=segment)
        # Otherwise we're all good
        return None