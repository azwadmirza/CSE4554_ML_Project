    def get_current_line_to_cursor(self):
        """Return text from prompt to cursor"""
        return self.get_text(self.current_prompt_pos, 'cursor')