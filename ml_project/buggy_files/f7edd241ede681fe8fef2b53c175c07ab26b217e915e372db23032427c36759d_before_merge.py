    def expand_default(self, option):
        default_value = None
        if self.parser is not None:
            self.parser._update_defaults(self.parser.defaults)
            default_value = self.parser.defaults.get(option.dest)
        help_text = optparse.IndentedHelpFormatter.expand_default(self, option)

        if default_value and option.metavar == 'URL':
            help_text = help_text.replace(
                default_value, redact_auth_from_url(default_value))

        return help_text