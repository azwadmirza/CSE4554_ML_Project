    def process_one_node(self, p, result, environment):
        '''Handle one node.'''
        c = self.c
        result.append(self.underline2(p))
        d = c.scanAllDirectives(p)
        if self.verbose:
            g.trace(d.get('language') or 'None', ':', p.h)
        s, code = self.process_directives(p.b, d)
        result.append(s)
        result.append('\n\n')
            # Add an empty line so bullet lists display properly.
        if code and self.execcode:
            s, err = self.exec_code(code, environment)
                # execute code found in a node, append to reST
            if not self.restoutput and s.strip():
                s = self.format_output(s) # if some non-reST to print
            result.append(s) # append, whether plain or reST output
            if err:
                err = self.format_output(err, prefix='**Error**::')
                result.append(err)