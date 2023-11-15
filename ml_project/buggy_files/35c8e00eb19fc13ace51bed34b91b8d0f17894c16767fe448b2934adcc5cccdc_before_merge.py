    def strformat(self, nlines_up=2):
        try:
            # Try to get a relative path
            # ipython/jupyter input just returns as self.filename
            path = os.path.relpath(self.filename)
        except ValueError:
            # Fallback to absolute path if error occurred in getting the
            # relative path.
            # This may happen on windows if the drive is different
            path = os.path.abspath(self.filename)

        lines = linecache.getlines(path)

        ret = [] # accumulates output
        if lines and self.line:

            def count_spaces(string):
                spaces = 0
                for x in itertools.takewhile(str.isspace, str(string)):
                    spaces += 1
                return spaces

            selected = lines[self.line - nlines_up:self.line]
            # see if selected contains a definition
            def_found = False
            for x in selected:
                if 'def ' in x:
                    def_found = True

            # no definition found, try and find one
            if not def_found:
                # try and find a def, go backwards from error line
                fn_name = None
                for x in reversed(lines[:self.line - 1]):
                    if 'def ' in x:
                        fn_name = x
                        break
                if fn_name:
                    ret.append(fn_name)
                    spaces = count_spaces(x)
                    ret.append(' '*(4 + spaces) + '<source elided>\n')

            ret.extend(selected[:-1])
            ret.append(_termcolor.highlight(selected[-1]))

            # point at the problem with a caret
            spaces = count_spaces(selected[-1])
            ret.append(' '*(spaces) + _termcolor.indicate("^"))

        # if in the REPL source may not be available
        if not ret:
            ret = "<source missing, REPL in use?>"

        err = _termcolor.filename('\nFile "%s", line %d:')+'\n%s'
        tmp = err % (path, self.line, _termcolor.code(''.join(ret)))
        return tmp