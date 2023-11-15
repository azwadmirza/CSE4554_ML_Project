    def _key_ctrl_space(self):
        """Action for Ctrl+Space"""
        if not self.is_completion_widget_visible():
            self.show_code_completion(automatic=False)