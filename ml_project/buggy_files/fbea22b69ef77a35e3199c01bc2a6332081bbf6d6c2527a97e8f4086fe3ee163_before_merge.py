    def tab_give(self, win_id: int = None):
        """Give the current tab to a new or existing window if win_id given.

        If no win_id is given, the tab will get detached into a new window.

        Args:
            win_id: The window ID of the window to give the current tab to.
        """
        if win_id == self._win_id:
            raise cmdexc.CommandError("Can't give a tab to the same window")

        if win_id is None:
            if self._count() < 2:
                raise cmdexc.CommandError("Cannot detach from a window with "
                                          "only one tab")

            tabbed_browser = self._new_tabbed_browser(
                private=self._tabbed_browser.private)
        else:
            tabbed_browser = objreg.get('tabbed-browser', scope='window',
                                        window=win_id)

        tabbed_browser.tabopen(self._current_url())
        self._tabbed_browser.close_tab(self._current_widget(), add_undo=False)