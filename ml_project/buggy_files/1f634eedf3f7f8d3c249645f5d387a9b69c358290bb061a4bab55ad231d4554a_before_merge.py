    def quote_type_string(self, type_string: str) -> str:
        """Quotes a type representation for use in messages."""
        no_quote_regex = r'^<(tuple|union): \d+ items>$'
        if (type_string in ['Module', 'overloaded function', '<nothing>', '<deleted>']
                or re.match(no_quote_regex, type_string) is not None):
            # Messages are easier to read if these aren't quoted.  We use a
            # regex to match strings with variable contents.
            return type_string
        return '"{}"'.format(type_string)