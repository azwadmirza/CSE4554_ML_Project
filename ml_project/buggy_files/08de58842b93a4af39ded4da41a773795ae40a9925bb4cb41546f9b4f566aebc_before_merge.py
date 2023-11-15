    def _key_tab(self):
        """Action for TAB key"""
        if self.is_cursor_on_last_line():
            empty_line = not self.get_current_line_to_cursor().strip()
            if empty_line:
                self.stdkey_tab()
            else:
                self.show_code_completion(automatic=False)