    def _parse_ctx_free(self, input, mode="exec", filename=None, logical_input=False):
        last_error_line = last_error_col = -1
        parsed = False
        original_error = None
        greedy = False
        if filename is None:
            filename = self.filename
        if logical_input:
            beg_spaces = starting_whitespace(input)
            input = input[len(beg_spaces) :]
        while not parsed:
            try:
                tree = self.parser.parse(
                    input,
                    filename=filename,
                    mode=mode,
                    debug_level=(self.debug_level > 2),
                )
                parsed = True
            except IndentationError as e:
                if original_error is None:
                    raise e
                else:
                    raise original_error
            except SyntaxError as e:
                if original_error is None:
                    original_error = e
                if (e.loc is None) or (
                    last_error_line == e.loc.lineno
                    and last_error_col in (e.loc.column + 1, e.loc.column)
                ):
                    raise original_error from None
                elif last_error_line != e.loc.lineno:
                    original_error = e
                last_error_col = e.loc.column
                last_error_line = e.loc.lineno
                idx = last_error_line - 1
                lines = input.splitlines()
                if input.endswith("\n"):
                    lines.append("")
                line, nlogical, idx = get_logical_line(lines, idx)
                if nlogical > 1 and not logical_input:
                    _, sbpline = self._parse_ctx_free(
                        line, mode=mode, filename=filename, logical_input=True
                    )
                    self._print_debug_wrapping(
                        line, sbpline, last_error_line, last_error_col, maxcol=None
                    )
                    replace_logical_line(lines, sbpline, idx, nlogical)
                    last_error_col += 3
                    input = "\n".join(lines)
                    continue
                if len(line.strip()) == 0:
                    # whitespace only lines are not valid syntax in Python's
                    # interactive mode='single', who knew?! Just ignore them.
                    # this might cause actual syntax errors to have bad line
                    # numbers reported, but should only affect interactive mode
                    del lines[idx]
                    last_error_line = last_error_col = -1
                    input = "\n".join(lines)
                    continue

                if last_error_line > 1 and lines[idx - 1].rstrip()[-1:] == ":":
                    # catch non-indented blocks and raise error.
                    prev_indent = len(lines[idx - 1]) - len(lines[idx - 1].lstrip())
                    curr_indent = len(lines[idx]) - len(lines[idx].lstrip())
                    if prev_indent == curr_indent:
                        raise original_error
                lexer = self.parser.lexer
                maxcol = (
                    None
                    if greedy
                    else find_next_break(line, mincol=last_error_col, lexer=lexer)
                )
                if not greedy and maxcol in (e.loc.column + 1, e.loc.column):
                    # go greedy the first time if the syntax error was because
                    # we hit an end token out of place. This usually indicates
                    # a subshell or maybe a macro.
                    if not balanced_parens(line, maxcol=maxcol):
                        greedy = True
                        maxcol = None
                sbpline = subproc_toks(
                    line, returnline=True, greedy=greedy, maxcol=maxcol, lexer=lexer
                )
                if sbpline is None:
                    # subprocess line had no valid tokens,
                    if len(line.partition("#")[0].strip()) == 0:
                        # likely because it only contained a comment.
                        del lines[idx]
                        last_error_line = last_error_col = -1
                        input = "\n".join(lines)
                        continue
                    elif not greedy:
                        greedy = True
                        continue
                    else:
                        # or for some other syntax error
                        raise original_error
                elif sbpline[last_error_col:].startswith(
                    "![!["
                ) or sbpline.lstrip().startswith("![!["):
                    # if we have already wrapped this in subproc tokens
                    # and it still doesn't work, adding more won't help
                    # anything
                    if not greedy:
                        greedy = True
                        continue
                    else:
                        raise original_error
                # replace the line
                self._print_debug_wrapping(
                    line, sbpline, last_error_line, last_error_col, maxcol=maxcol
                )
                replace_logical_line(lines, sbpline, idx, nlogical)
                last_error_col += 3
                input = "\n".join(lines)
        if logical_input:
            input = beg_spaces + input
        return tree, input