    def md_process_directives(self, s, d):
        """s is string to process, d is dictionary of directives at the node."""
        trace = False and not g.unitTesting
        lang = d.get('language') or 'python' # EKR.
        codeflag = lang != 'md' # EKR
        lines = g.splitLines(s)
        result = []
        code = ''
        if codeflag and self.showcode:
            result.append(self.md_code_directive(lang)) # EKR
        for s in lines:
            if s.startswith('@'):
                i = g.skip_id(s, 1)
                word = s[1: i]
                # Add capability to detect mid-node language directives (not really that useful).
                # Probably better to just use a code directive.  "execute-script" is not possible.
                # If removing, ensure "if word in g.globalDirectiveList:  continue" is retained
                # to stop directive being put into the reST output.
                if word == 'language' and not codeflag: # only if not already code
                    lang = s[i:].strip()
                    codeflag = lang in ['python',]
                    if codeflag:
                        if self.verbose:
                            g.es('New code section within node:', lang)
                        if self.showcode:
                            result.append(self.md_code_directive(lang)) # EKR
                    else:
                        result.append('\n\n')
                    continue
                elif word in g.globalDirectiveList:
                    continue
            if codeflag:
                emit_line = not (s.startswith('@') or s.startswith('<<')) if self.code_only else True
                if self.showcode and emit_line:
                    result.append('    ' + s) # 4 space indent on each line
                code += s # accumulate code lines for execution
            else:
                if not self.code_only:
                    result.append(s)
        result = ''.join(result)
        if trace: g.trace('result:\n', result) # ,'\ncode:',code)
        return result, code