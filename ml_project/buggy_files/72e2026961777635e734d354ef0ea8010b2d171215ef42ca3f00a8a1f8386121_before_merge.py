    def _add_regex(self, name, re):
        reg = Vte.Regex.new_for_match(re, len(re), self.regex_flags)
        self.matches[name] = self.vte.match_add_regex(reg, 0)
        self.vte.match_set_cursor_name(self.matches[name], 'pointer')