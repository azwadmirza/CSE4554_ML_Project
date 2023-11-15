    def _update_palette(self, event):
        """Update the napari GUI theme."""
        # template and apply the primary stylesheet
        themed_stylesheet = template(
            self.raw_stylesheet, **self.viewer.palette
        )
        if self._console is not None:
            self.console._update_palette(
                self.viewer.palette, themed_stylesheet
            )
        self.setStyleSheet(themed_stylesheet)
        self.canvas.bgcolor = self.viewer.palette['canvas']