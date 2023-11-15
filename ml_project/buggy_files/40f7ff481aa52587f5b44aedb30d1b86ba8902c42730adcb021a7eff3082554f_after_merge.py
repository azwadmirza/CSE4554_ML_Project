    def refresh(self, inicontents=None):
        comment_count = 1
        unknown_count = 1
        curr_indent = ''
        inicontents = inicontents or self.inicontents
        inicontents = inicontents.strip(os.linesep)

        if not inicontents:
            return
        for opt in self:
            self.pop(opt)
        for opt_str in inicontents.split(os.linesep):
            # Match comments
            com_match = COM_REGX.match(opt_str)
            if com_match:
                name = '#comment{0}'.format(comment_count)
                self.com = com_match.group(1)
                comment_count += 1
                self.update({name: opt_str})
                continue
            # Add indented lines to the value of the previous entry.
            indented_match = INDENTED_REGX.match(opt_str)
            if indented_match:
                indent = indented_match.group(1).replace('\t', '    ')
                if indent > curr_indent:
                    options = list(self)
                    if options:
                        prev_opt = options[-1]
                        value = self.get(prev_opt)
                        self.update({prev_opt: os.linesep.join((value, opt_str))})
                    continue
            # Match normal key+value lines.
            opt_match = self.opt_regx.match(opt_str)
            if opt_match:
                curr_indent, name, self.sep, value = opt_match.groups()
                curr_indent = curr_indent.replace('\t', '    ')
                self.update({name: value})
                continue
            # Anything remaining is a mystery.
            name = '#unknown{0}'.format(unknown_count)
            self.update({name: opt_str})
            unknown_count += 1