    def _update_favicons(self):
        """Update favicons when config was changed."""
        for tab in self.widgets():
            self.widget.update_tab_favicon(tab)