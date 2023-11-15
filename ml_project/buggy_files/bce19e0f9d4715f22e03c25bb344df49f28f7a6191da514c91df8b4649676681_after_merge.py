    def _key_period(self, text):
        """Action for '.'"""
        self.insert_text(text)
        if self.codecompletion_auto:
            # Enable auto-completion only if last token isn't a float
            last_obj = self.get_last_obj()
            if last_obj and not last_obj.isdigit():
                self.show_code_completion()