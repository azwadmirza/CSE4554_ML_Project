    def md_process_one_node(self, p, result, environment):
        '''Handle one node.'''
        c = self.c
        if not self.code_only:
            result.append(self.md_underline2(p))
        d = c.scanAllDirectives(p)
        if self.verbose:
            g.trace(d.get('language') or 'None', ':', p.h)
        s, code = self.md_process_directives(p.b, d)
        result.append(s)
        result.append('\n\n')
            # Add an empty line so bullet lists display properly.
        if code and self.execcode:
            s, err = self.md_exec_code(code, environment)
                # execute code found in a node, append to md
            if not self.restoutput and s.strip():
                s = self.md_format_output(s) # if some non-md to print
            result.append(s) # append, whether plain or md output
            if err:
                err = self.md_format_output(err, prefix='**Error**:')
                result.append(err)