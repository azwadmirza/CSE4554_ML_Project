    def _parse_ctx_free(self, input, mode='exec'):
        last_error_line = last_error_col = -1
        parsed = False
        original_error = None
        while not parsed:
            try:
                tree = self.parser.parse(input,
                                         filename=self.filename,
                                         mode=mode,
                                         debug_level=(self.debug_level > 1))
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
                    raise original_error
                last_error_col = e.loc.column
                last_error_line = e.loc.lineno
                idx = last_error_line - 1
                lines = input.splitlines()
                line = lines[idx]
                if input.endswith('\n'):
                    lines.append('')
                if len(line.strip()) == 0:
                    # whitespace only lines are not valid syntax in Python's
                    # interactive mode='single', who knew?! Just ignore them.
                    # this might cause actual sytax errors to have bad line
                    # numbers reported, but should only effect interactive mode
                    del lines[idx]
                    last_error_line = last_error_col = -1
                    input = '\n'.join(lines)
                    continue

                if last_error_line > 1 and lines[idx-1].rstrip()[-1:] == ':':
                    # catch non-indented blocks and raise error.
                    prev_indent = len(lines[idx-1]) - len(lines[idx-1].lstrip())
                    curr_indent = len(lines[idx]) - len(lines[idx].lstrip())
                    if prev_indent == curr_indent:
                        raise original_error
                lexer = self.parser.lexer
                maxcol = find_next_break(line, mincol=last_error_col,
                                         lexer=lexer)
                sbpline = subproc_toks(line, returnline=True,
                                       maxcol=maxcol, lexer=lexer)
                if sbpline is None:
                    # subprocess line had no valid tokens,
                    if len(line.partition('#')[0].strip()) == 0:
                        # likely because it only contained a comment.
                        del lines[idx]
                        last_error_line = last_error_col = -1
                        input = '\n'.join(lines)
                        continue
                    else:
                        # or for some other syntax error
                        raise original_error
                elif sbpline[last_error_col:].startswith('![![') or \
                        sbpline.lstrip().startswith('![!['):
                    # if we have already wrapped this in subproc tokens
                    # and it still doesn't work, adding more won't help
                    # anything
                    raise original_error
                else:
                    if self.debug_level:
                        msg = ('{0}:{1}:{2}{3} - {4}\n'
                               '{0}:{1}:{2}{3} + {5}')
                        mstr = '' if maxcol is None else ':' + str(maxcol)
                        msg = msg.format(self.filename, last_error_line,
                                         last_error_col, mstr, line, sbpline)
                        print(msg, file=sys.stderr)
                    lines[idx] = sbpline
                last_error_col += 3
                input = '\n'.join(lines)
        return tree, input