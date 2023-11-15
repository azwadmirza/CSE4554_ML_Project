    def fullscreen(self, leave=False):
        """Toggle fullscreen mode.

        Args:
            leave: Only leave fullscreen if it was entered by the page.
        """
        if leave:
            tab = self._current_widget()
            try:
                tab.action.exit_fullscreen()
            except browsertab.UnsupportedOperationError:
                pass
            return

        window = self._tabbed_browser.window()
        window.setWindowState(window.windowState() ^ Qt.WindowFullScreen)