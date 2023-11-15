    def display_help(self, help_text, clicked):
        editor = self.get_current_editor()
        if clicked:
            name = editor.get_last_hover_word()
        else:
            name = editor.get_current_word()

        editor.sig_display_object_info.disconnect(self.display_help)
        self.help.switch_to_editor_source()
        self.send_to_help(name, help_text, force=True)