    def refresh_table(self, interrupt=False):
        """Refresh variable table"""
        if self.is_visible and self.isVisible():
            self.shellwidget.refresh_namespacebrowser(interrupt=interrupt)
            try:
                self.editor.resizeRowToContents()
            except TypeError:
                pass