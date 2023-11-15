    def format_stack_entry(self, frame_lineno, lprefix=': ', context = 3):
        import repr

        ret = []

        Colors = self.color_scheme_table.active_colors
        ColorsNormal = Colors.Normal
        tpl_link = u'%s%%s%s' % (Colors.filenameEm, ColorsNormal)
        tpl_call = u'%s%%s%s%%s%s' % (Colors.vName, Colors.valEm, ColorsNormal)
        tpl_line = u'%%s%s%%s %s%%s' % (Colors.lineno, ColorsNormal)
        tpl_line_em = u'%%s%s%%s %s%%s%s' % (Colors.linenoEm, Colors.line,
                                            ColorsNormal)

        frame, lineno = frame_lineno

        return_value = ''
        if '__return__' in frame.f_locals:
            rv = frame.f_locals['__return__']
            #return_value += '->'
            return_value += repr.repr(rv) + '\n'
        ret.append(return_value)

        #s = filename + '(' + `lineno` + ')'
        filename = self.canonic(frame.f_code.co_filename)
        link = tpl_link % py3compat.cast_unicode(filename)

        if frame.f_code.co_name:
            func = frame.f_code.co_name
        else:
            func = "<lambda>"

        call = ''
        if func != '?':
            if '__args__' in frame.f_locals:
                args = repr.repr(frame.f_locals['__args__'])
            else:
                args = '()'
            call = tpl_call % (func, args)

        # The level info should be generated in the same format pdb uses, to
        # avoid breaking the pdbtrack functionality of python-mode in *emacs.
        if frame is self.curframe:
            ret.append('> ')
        else:
            ret.append('  ')
        ret.append(u'%s(%s)%s\n' % (link,lineno,call))

        start = lineno - 1 - context//2
        lines = ulinecache.getlines(filename)
        start = max(start, 0)
        start = min(start, len(lines) - context)
        lines = lines[start : start + context]

        for i,line in enumerate(lines):
            show_arrow = (start + 1 + i == lineno)
            linetpl = (frame is self.curframe or show_arrow) \
                      and tpl_line_em \
                      or tpl_line
            ret.append(self.__format_line(linetpl, filename,
                                          start + 1 + i, line,
                                          arrow = show_arrow) )
        return ''.join(ret)