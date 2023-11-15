    def _parse_ctx_free(self, input, mode='exec', filename=None):
        last_error_line = last_error_col = -1
        parsed = False
        original_error = None
        greedy = False
        if filename is None:
            filename = self.filename
        while not parsed:
            try:
                tree = self.parser.parse(input,
                                         filename=filename,
                                         mode=mode,
                                         debug_level=(self.debug_level > 2))
                parsed = True
            except IndentationError as e:
                if original_error is None:
                    raise e
                else:
                    raise original_error
            except SyntaxError as e:
                if original_error is None:
                    original_error = e
                if (e.loc is None) or (last_error_line == e.loc.lineno and
                                       last_error_col in (e.loc.column + 1,
                                                          e.loc.column)):
                    raise original_error from None
                last_error_col = e.loc.column
                last_error_line = e.loc.lineno
                idx = last_error_line - 1
                lines = input.splitlines()
                line, nlogical, idx = get_logical_line(lines, idx)
                if input.endswith('\n'):
                    lines.append('')
                if len(line.strip()) == 0:
                    # whitespace only lines are not valid syntax in Python's
                    # interactive mode='single', who knew?! Just ignore them.
                    # this might cause actual syntax errors to have bad line
                    # numbers reported, but should only affect interactive mode
                    del lines[idx]
                    last_error_line = last_error_col = -1
                    input = '\n'.join(lines)
                    continue

                if last_error_line > 1 and lines[idx - 1].rstrip()[-1:] == ':':
                    # catch non-indented blocks and raise error.
                    prev_indent = len(lines[idx - 1]) - len(lines[idx - 1].lstrip())
                    curr_indent = len(lines[idx]) - len(lines[idx].lstrip())
                    if prev_indent == curr_indent:
                        raise original_error
                lexer = self.parser.lexer
                maxcol = None if greedy else find_next_break(line,
                                                             mincol=last_error_col,
                                                             lexer=lexer)
                if not greedy and maxcol in (e.loc.column + 1, e.loc.column):
                    # go greedy the first time if the syntax error was because
                    # we hit an end token out of place. This usually indicates
                    # a subshell or maybe a macro.
                    if not balanced_parens(line, maxcol=maxcol):
                        greedy = True
                        maxcol = None
                sbpline = subproc_toks(line, returnline=True, greedy=greedy,
                                       maxcol=maxcol, lexer=lexer)
                if sbpline is None:
                    # subprocess line had no valid tokens,
                    if len(line.partition('#')[0].strip()) == 0:
                        # likely because it only contained a comment.
                        del lines[idx]
                        last_error_line = last_error_col = -1
                        input = '\n'.join(lines)
                        continue
                    elif not greedy:
                        greedy = True
                        continue
                    else:
                        # or for some other syntax error
                        raise original_error
                elif sbpline[last_error_col:].startswith('![![') or \
                        sbpline.lstrip().startswith('![!['):
                    # if we have already wrapped this in subproc tokens
                    # and it still doesn't work, adding more won't help
                    # anything
                    if not greedy:
                        greedy = True
                        continue
                    else:
                        raise original_error
                else:
                    # print some debugging info
                    if self.debug_level > 1:
                        msg = ('{0}:{1}:{2}{3} - {4}\n'
                               '{0}:{1}:{2}{3} + {5}')
                        mstr = '' if maxcol is None else ':' + str(maxcol)
                        msg = msg.format(self.filename, last_error_line,
                                         last_error_col, mstr, line, sbpline)
                        print(msg, file=sys.stderr)
                    # replace the line
                    replace_logical_line(lines, sbpline, idx, nlogical)
                last_error_col += 3
                input = '\n'.join(lines)
        return tree, input