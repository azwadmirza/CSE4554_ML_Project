    def process_signatures(self, params):
        # self.hide_completion_widget()
        signature = params['params']
        if (signature is not None and
                'activeParameter' in signature):
            self.sig_signature_invoked.emit()
            line, _ = self.get_cursor_line_column()
            active_parameter_idx = signature['activeParameter']
            signature = signature['signatures']
            func_doc = signature['documentation']
            func_signature = signature['label']
            parameters = signature['parameters']
            parameter = parameters[active_parameter_idx]

            font = self.font()
            size = font.pointSize()
            family = font.family()

            parameter_str = ''
            color_change_str = ('<span style=\'font-family: "{0}"; '
                                'font-size: {1}pt; color: {2}\'>')
            if (parameter['documentation'] is not None and
                    len(parameter['documentation']) > 0):
                parameter_fmt = ('{0}<b>{1}</b></span>: {2}\n')
                parameter_str = parameter_fmt.format(
                    color_change_str.format(family, size, '#daa520'),
                    parameter['label'], parameter['documentation'])

            title = func_signature.replace(
                parameter['label'], '{0}{1}</span>'.format(
                    color_change_str.format(family, size, '#daa520'),
                    parameter['label']))
            tooltip_text = "{0}{1}".format(parameter_str, func_doc)
            self.show_calltip(
                title, tooltip_text, color='#999999')