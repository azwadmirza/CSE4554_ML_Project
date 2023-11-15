    def has_markers(self):
        """Return True if this editorstack has a marker margin for TODOs or
        code analysis"""
        return self.todolist_enabled or self.pyflakes_enabled\
               or self.pep8_enabled