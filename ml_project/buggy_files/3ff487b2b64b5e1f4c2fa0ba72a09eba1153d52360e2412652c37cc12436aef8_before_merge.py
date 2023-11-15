    def _current_widget(self):
        """Get the currently active widget from a command."""
        widget = self._tabbed_browser.currentWidget()
        if widget is None:
            raise cmdexc.CommandError("No WebView available yet!")
        return widget