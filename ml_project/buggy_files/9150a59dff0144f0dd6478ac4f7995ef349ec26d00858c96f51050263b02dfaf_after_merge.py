    def _tab_focus_last(self, *, show_error=True):
        """Select the tab which was last focused."""
        try:
            tab = objreg.get('last-focused-tab', scope='window',
                             window=self._win_id)
        except KeyError:
            if not show_error:
                return
            raise cmdexc.CommandError("No last focused tab!")
        idx = self._tabbed_browser.widget.indexOf(tab)
        if idx == -1:
            raise cmdexc.CommandError("Last focused tab vanished!")
        self._set_current_index(idx)