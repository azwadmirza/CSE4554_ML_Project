    def _parse_ctx_free(self, input, mode='exec'):
        last_error_line = last_error_col = -1
        parsed = False
        original_error = None
        while not parsed:
            try:
                tree = self.parser.parse(input,
                                         filename=self.filename,
                                         mode=mode,
                                         debug_level=self.debug_level)
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
                maxcol = line.find(';', last_error_col)
                maxcol = None if maxcol < 0 else maxcol + 1
                sbpline = subproc_toks(line,
                                       returnline=True,
                                       maxcol=maxcol,
                                       lexer=self.parser.lexer)
                if sbpline is None:
                    # subprocess line had no valid tokens, likely because
                    # it only contained a comment.
                    del lines[idx]
                    last_error_line = last_error_col = -1
                    input = '\n'.join(lines)
                    continue
                else:
                    lines[idx] = sbpline
                last_error_col += 3
                input = '\n'.join(lines)
        return tree