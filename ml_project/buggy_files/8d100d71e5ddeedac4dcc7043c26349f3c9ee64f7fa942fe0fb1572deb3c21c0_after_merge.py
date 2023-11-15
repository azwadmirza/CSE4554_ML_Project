    def _editor_shell_command(self, filename):
        EDITOR = os.environ.get('EDITOR','vi')
        editor = shlex.split(EDITOR)
        editor.append(filename)

        return editor