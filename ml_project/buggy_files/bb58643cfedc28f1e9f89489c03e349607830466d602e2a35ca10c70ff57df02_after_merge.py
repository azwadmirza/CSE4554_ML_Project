    def get_set_string(self):
        value = self.raw_value

        # For string value, convert utf8 byte string to unicode.
        if isinstance(value, six.binary_type):
            value = codecs.decode(value, 'utf-8')

        # Remove surrounded ' and " characters
        if isinstance(value, six.string_types):
            # The first character must be ' or " and ends with the same character.
            # See PR #404 for more information
            pattern = r"^(?P<quote>[\"'])(?P<content>.*?)(?P=quote)$"

            value = re.sub(pattern, r"\g<content>", value)

        # Write back to self.value
        self.value = value

        for trigger in triggers[self.name]:
            trigger()

        if not pwndbg.decorators.first_prompt:
            # Remove the newline that gdb adds automatically
            return '\b'
        return 'Set %s to %r' % (self.docstring, self.value)