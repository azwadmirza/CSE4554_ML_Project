    def display_help(self, help_text, clicked):
        editor = self.get_current_editor()
        if clicked:
            name = editor.get_last_hover_word()
        else:
            name = editor.get_current_word()

        try:
            editor.sig_display_object_info.disconnect(self.display_help)
        except TypeError:
            # Needed to prevent an error after some time in idle.
            # See spyder-ide/spyder#11228
            pass
        self.help.switch_to_editor_source()
        self.send_to_help(name, help_text, force=True)