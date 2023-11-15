    def valid_project(self):
        """Handle an invalid active project."""
        if bool(self.projects.get_active_project_path()):
            path = self.projects.get_active_project_path()
            if not self.projects.is_valid_project(path):
                if path:
                    QMessageBox.critical(
                        self,
                        _('Error'),
                        _("<b>{}</b> is no longer a valid Spyder project! "
                          "Since it is the current active project, it will "
                          "be closed automatically.").format(path))
                self.projects.close_project()