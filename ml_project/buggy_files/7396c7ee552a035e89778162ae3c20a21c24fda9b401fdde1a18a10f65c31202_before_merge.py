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

                # Does the line contain a place where an indent might be possible?
                if any(elem.is_meta and elem.indent_val != 0 for elem in this_line):
                    # What's the net sum of them?
                    indent_balance = sum(elem.indent_val for elem in this_line if elem.is_meta)
                    # Yes, let's work out which is best.
                    if indent_balance == 0:
                        # It's even. We should break after the *last* dedent
                        ws_pre = []
                        ws_post = []
                        running_balance = 0
                        started = False
                        found = False
                        fix_buffer = None
                        # Work through to find the right point
                        for elem in this_line:
                            if elem.name == 'whitespace':
                                if found:
                                    if fix_buffer is None:
                                        # In this case we EDIT, because
                                        # we want to remove the existing whitespace
                                        # here. We need to remember the INDENT.
                                        fix_buffer = [
                                            LintFix(
                                                'edit', elem,
                                                [segment] + line_indent
                                            )
                                        ]
                                    else:
                                        # Store potentially unnecessary whitespace.
                                        ws_post.append(elem)
                                elif started:
                                    # Store potentially unnecessary whitespace.
                                    ws_pre.append(elem)
                            elif elem.is_meta:
                                running_balance += elem.indent_val
                                started = True
                                # Clear the buffer.
                                ws_post = []
                                if running_balance == 0:
                                    found = True
                            else:
                                # Something that isn't a meta or whitespace
                                if found:
                                    if fix_buffer is None:
                                        # In this case we create because we
                                        # want to preserve what already exits
                                        # here. We need to remember the INDENT.
                                        fix_buffer = [
                                            LintFix(
                                                'create', elem,
                                                [segment] + line_indent
                                            )
                                        ]
                                    # We have all we need
                                    break
                                else:
                                    # Clear the buffer.
                                    ws_pre = []
                        else:
                            raise RuntimeError("We shouldn't get here!")

                        # Remove unnecessary whitespace
                        for elem in ws_pre + ws_post:
                            fix_buffer.append(
                                LintFix(
                                    'delete', elem
                                )
                            )

                        return LintResult(anchor=segment, fixes=fix_buffer)
                    elif indent_balance > 0:
                        # If it's positive, we have more indents than dedents.
                        # Make sure the first unused indent is used.
                        delete_buffer = []
                        newline_anchor = None
                        found = False
                        for elem in this_line:
                            if elem.name == 'whitespace':
                                delete_buffer.append(elem)
                            elif found:
                                newline_anchor = elem
                                break
                            elif elem.is_meta:
                                if elem.indent_val > 0:
                                    found = True
                                else:
                                    pass
                            else:
                                # It's not meta, and not whitespace:
                                # reset buffer
                                delete_buffer = []
                        else:
                            raise RuntimeError("We shouldn't get here!")

                        # Make a newline where it needs to be, with ONE EXTRA INDENT
                        new_indent = self._make_indent(1)
                        fix_buffer = [
                            LintFix(
                                'create', newline_anchor,
                                # It's ok to use the current segment posmarker, because we're staying in the same statement (probably?)
                                [segment] + line_indent + [self.make_whitespace(raw=new_indent, pos_marker=segment.pos_marker)]
                            )
                        ]

                        # Remove unnecessary whitespace
                        for elem in delete_buffer:
                            fix_buffer.append(
                                LintFix(
                                    'delete', elem
                                )
                            )

                        return LintResult(anchor=segment, fixes=fix_buffer)
                    else:
                        # Don't know what to do here!
                        raise NotImplementedError(
                            ("Don't know what to do with negative "
                             "indent balance ({0}).").format(
                                indent_balance))

                return LintResult(anchor=segment)
        # Otherwise we're all good
        return None