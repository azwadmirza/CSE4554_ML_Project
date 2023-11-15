    def edit_command(self, run=False):
        """Open an editor to modify the current command.

        Args:
            run: Run the command if the editor exits successfully.
        """
        ed = editor.ExternalEditor(parent=self)

        def callback(text):
            if not text or text[0] not in modeparsers.STARTCHARS:
                message.error('command must start with one of {}'
                              .format(modeparsers.STARTCHARS))
                return
            self.set_cmd_text(text)
            if run:
                self.command_accept()

        ed.editing_finished.connect(callback)
        ed.edit(self.text())