    def clearerrors(self, level=logger.ERROR):
        """Clear the errors or warnings."""
        if int(level) == logger.WARNING:
            classes.WarningViewer.clear()
        else:
            classes.ErrorViewer.clear()

        return self.redirect('/errorlogs/viewlog/')