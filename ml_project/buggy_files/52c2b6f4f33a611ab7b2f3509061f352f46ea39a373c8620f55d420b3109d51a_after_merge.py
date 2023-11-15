    def resizeEvent(self, e):
        """Extend resizewindow's resizeEvent to adjust completion.

        Args:
            e: The QResizeEvent
        """
        super().resizeEvent(e)
        self._update_overlay_geometries()
        self._downloadview.updateGeometry()
        self.tabbed_browser.widget.tabBar().refresh()