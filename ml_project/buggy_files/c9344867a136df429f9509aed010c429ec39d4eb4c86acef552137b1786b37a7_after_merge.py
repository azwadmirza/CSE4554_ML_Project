    def execute_in_external_console(self, lines, focus_to_editor):
        """
        Execute lines in external or IPython console and eventually set focus
        to the editor
        """
        console = self.extconsole
        if self.ipyconsole is None or self.last_console_plugin_focus_was_python:
            console = self.extconsole
        else:
            console = self.ipyconsole
        console.visibility_changed(True)
        console.raise_()
        console.execute_python_code(lines)
        if focus_to_editor:
            self.editor.visibility_changed(True)