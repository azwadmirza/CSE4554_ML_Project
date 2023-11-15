    def get_signature(self, content):
        """Get signature from inspect reply content"""
        data = content.get('data', {})
        text = data.get('text/plain', '')
        if text:
            text = ANSI_OR_SPECIAL_PATTERN.sub('', text)
            self._control.current_prompt_pos = self._prompt_pos
            line = self._control.get_current_line_to_cursor()
            name = line[:-1].split('(')[-1]   # Take last token after a (
            name = name.split('.')[-1]        # Then take last token after a .
            # Clean name from invalid chars
            try:
                name = self.clean_invalid_var_chars(name)
            except:
                pass
            text = text.split('Docstring:')[-1]
            argspec = getargspecfromtext(text)
            if argspec:
                # This covers cases like np.abs, whose docstring is
                # the same as np.absolute and because of that a proper
                # signature can't be obtained correctly
                signature = name + argspec
            else:
                signature = getsignaturefromtext(text, name)
            # Remove docstring for uniformity with editor
            signature = signature.split('Docstring:')[0]

            return signature
        else:
            return ''