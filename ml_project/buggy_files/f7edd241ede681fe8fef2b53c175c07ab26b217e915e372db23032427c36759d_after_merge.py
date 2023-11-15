    def expand_default(self, option):
        default_values = None
        if self.parser is not None:
            self.parser._update_defaults(self.parser.defaults)
            default_values = self.parser.defaults.get(option.dest)
        help_text = optparse.IndentedHelpFormatter.expand_default(self, option)

        if default_values and option.metavar == 'URL':
            if isinstance(default_values, string_types):
                default_values = [default_values]

            # If its not a list, we should abort and just return the help text
            if not isinstance(default_values, list):
                default_values = []

            for val in default_values:
                help_text = help_text.replace(
                    val, redact_auth_from_url(val))

        return help_text