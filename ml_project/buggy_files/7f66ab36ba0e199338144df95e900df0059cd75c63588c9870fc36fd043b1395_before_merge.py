    def _draw_regs(self):
        longest_label_width = 0
        if self.initial_state:
            initial_qbit = ' |0>'
            initial_cbit = ' 0'
        else:
            initial_qbit = ''
            initial_cbit = ''

        def _fix_double_script(label):
            words = label.split(' ')
            words = [word.replace('_', r'\_') if word.count('_') > 1 else word
                     for word in words]
            words = [word.replace('^', r'\^{\ }') if word.count('^') > 1 else word
                     for word in words]
            label = ' '.join(words).replace(' ', '\\;')
            return label

        # quantum register
        for ii, reg in enumerate(self._qreg):
            if len(self._qreg) > 1:
                if self.layout is None:
                    label = '${{{name}}}_{{{index}}}$'.format(name=reg.register.name,
                                                              index=reg.index)
                    label = _fix_double_script(label) + initial_qbit
                    text_width = self._get_text_width(label, self._style.fs)
                else:
                    label = '${{{name}}}_{{{index}}} \\mapsto {{{physical}}}$'.format(
                        name=self.layout[reg.index].register.name,
                        index=self.layout[reg.index].index, physical=reg.index)
                    label = _fix_double_script(label) + initial_qbit
                    text_width = self._get_text_width(label, self._style.fs)
            else:
                label = '{name}'.format(name=reg.register.name)
                label = _fix_double_script(label) + initial_qbit
                text_width = self._get_text_width(label, self._style.fs)

            text_width = text_width * 1.15  # to account for larger font used
            if text_width > longest_label_width:
                longest_label_width = text_width

            pos = -ii
            self._qreg_dict[ii] = {
                'y': pos, 'label': label, 'index': reg.index, 'group': reg.register}
            self._cond['n_lines'] += 1

        # classical register
        if self._creg:
            n_creg = self._creg.copy()
            n_creg.pop(0)
            idx = 0
            y_off = -len(self._qreg)
            for ii, (reg, nreg) in enumerate(itertools.zip_longest(self._creg, n_creg)):
                pos = y_off - idx
                if self.cregbundle:
                    label = '{}'.format(reg.register.name)
                    label = _fix_double_script(label) + initial_cbit
                    text_width = self._get_text_width(reg.register.name, self._style.fs) * 1.15
                    if text_width > longest_label_width:
                        longest_label_width = text_width
                    self._creg_dict[ii] = {'y': pos, 'label': label, 'index': reg.index,
                                           'group': reg.register}
                    if not (not nreg or reg.register != nreg.register):
                        continue
                else:
                    label = '${}_{{{}}}$'.format(reg.register.name, reg.index)
                    label = _fix_double_script(label) + initial_cbit
                    text_width = self._get_text_width(reg.register.name, self._style.fs) * 1.15
                    if text_width > longest_label_width:
                        longest_label_width = text_width
                    self._creg_dict[ii] = {'y': pos, 'label': label, 'index': reg.index,
                                           'group': reg.register}
                self._cond['n_lines'] += 1
                idx += 1

        self._reg_long_text = longest_label_width
        self.x_offset = -1.2 + self._reg_long_text