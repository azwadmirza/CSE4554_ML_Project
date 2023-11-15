    def edit_command(self, run=False):
        """Open an editor to modify the current command.

        Args:
            run: Run the command if the editor exits successfully.
        """
        ed = editor.ExternalEditor(parent=self)

        def callback(text):
            self.set_cmd_text(text)
            if run:
                self.command_accept()

        ed.editing_finished.connect(callback)
        ed.edit(self.text())