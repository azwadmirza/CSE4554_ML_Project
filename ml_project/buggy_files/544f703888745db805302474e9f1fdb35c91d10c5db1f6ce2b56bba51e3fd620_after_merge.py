    def _format_signature(self, signatures, parameter=None,
                          parameter_color=_PARAMETER_HIGHLIGHT_COLOR,
                          char_color=_CHAR_HIGHLIGHT_COLOR):
        """
        Create HTML template for signature.

        This template will include indent after the method name, a highlight
        color for the active parameter and highlights for special chars.

        Special chars depend on the language.
        """
        active_parameter_template = (
            '<span style=\'font-family:"{font_family}";'
            'font-size:{font_size}pt;'
            'color:{color}\'>'
            '<b>{parameter}</b>'
            '</span>'
        )
        chars_template = (
            '<span style="color:{0};'.format(self._CHAR_HIGHLIGHT_COLOR) +
            'font-weight:bold">{char}'
            '</span>'
        )

        def handle_sub(matchobj):
            """
            Handle substitution of active parameter template.

            This ensures the correct highlight of the active parameter.
            """
            match = matchobj.group(0)
            new = match.replace(parameter, active_parameter_template)
            return new

        if not isinstance(signatures, list):
            signatures = [signatures]

        new_signatures = []
        for signature in signatures:
            # Remove duplicate spaces
            signature = ' '.join(signature.split())

            # Replace initial spaces
            signature = signature.replace('( ', '(')

            # Process signature template
            if parameter:
                pattern = r'[\*|(|\s](' + parameter + r')[,|)|\s|=]'

            formatted_lines = []
            name = signature.split('(')[0]
            indent = ' ' * (len(name) + 1)
            rows = textwrap.wrap(signature, width=60, subsequent_indent=indent)
            for row in rows:
                if parameter:
                    # Add template to highlight the active parameter
                    row = re.sub(pattern, handle_sub, row)

                row = row.replace(' ', '&nbsp;')
                row = row.replace('span&nbsp;', 'span ')

                language = getattr(self, 'language', None)
                if language and 'python' == language.lower():
                    for char in ['(', ')', ',', '*', '**']:
                        new_char = chars_template.format(char=char)
                        row = row.replace(char, new_char)

                formatted_lines.append(row)
            title_template = '<br>'.join(formatted_lines)

            # Get current font properties
            font = self.font()
            font_size = font.pointSize()
            font_family = font.family()

            # Format title to display active parameter
            if parameter:
                title = title_template.format(
                    font_size=font_size,
                    font_family=font_family,
                    color=parameter_color,
                    parameter=parameter,
                )
            else:
                title = title_template
            new_signatures.append(title)

        return '<br><br>'.join(new_signatures)