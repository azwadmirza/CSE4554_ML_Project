    def lex(self, subdir):
        line_start = 0
        lineno = 1
        loc = 0
        par_count = 0
        bracket_count = 0
        col = 0
        while loc < len(self.code):
            matched = False
            value = None
            for (tid, reg) in self.token_specification:
                mo = reg.match(self.code, loc)
                if mo:
                    curline = lineno
                    curline_start = line_start
                    col = mo.start() - line_start
                    matched = True
                    span_start = loc
                    loc = mo.end()
                    span_end = loc
                    bytespan = (span_start, span_end)
                    match_text = mo.group()
                    if tid == 'ignore' or tid == 'comment':
                        break
                    elif tid == 'lparen':
                        par_count += 1
                    elif tid == 'rparen':
                        par_count -= 1
                    elif tid == 'lbracket':
                        bracket_count += 1
                    elif tid == 'rbracket':
                        bracket_count -= 1
                    elif tid == 'dblquote':
                        raise ParseException('Double quotes are not supported. Use single quotes.', self.getline(line_start), lineno, col)
                    elif tid == 'string':
                        # Handle here and not on the regexp to give a better error message.
                        if match_text.find("\n") != -1:
                            mlog.warning("""Newline character in a string detected, use ''' (three single quotes) for multiline strings instead.
This will become a hard error in a future Meson release.""", self.getline(line_start), lineno, col)
                        value = match_text[1:-1]
                        value = ESCAPE_SEQUENCE_SINGLE_RE.sub(decode_match, value)
                    elif tid == 'multiline_string':
                        tid = 'string'
                        value = match_text[3:-3]
                        value = ESCAPE_SEQUENCE_MULTI_RE.sub(decode_match, value)
                        lines = match_text.split('\n')
                        if len(lines) > 1:
                            lineno += len(lines) - 1
                            line_start = mo.end() - len(lines[-1])
                    elif tid == 'number':
                        value = int(match_text)
                    elif tid == 'hexnumber':
                        tid = 'number'
                        value = int(match_text, base=16)
                    elif tid == 'eol' or tid == 'eol_cont':
                        lineno += 1
                        line_start = loc
                        if par_count > 0 or bracket_count > 0:
                            break
                    elif tid == 'id':
                        if match_text in self.keywords:
                            tid = match_text
                        else:
                            value = match_text
                    yield Token(tid, subdir, curline_start, curline, col, bytespan, value)
                    break
            if not matched:
                raise ParseException('lexer', self.getline(line_start), lineno, col)