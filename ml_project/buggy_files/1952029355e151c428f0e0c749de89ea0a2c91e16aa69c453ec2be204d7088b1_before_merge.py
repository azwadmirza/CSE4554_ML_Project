    def tab_only(self, prev=False, next_=False, force=False):
        """Close all tabs except for the current one.

        Args:
            prev: Keep tabs before the current.
            next_: Keep tabs after the current.
            force: Avoid confirmation for pinned tabs.
        """
        cmdutils.check_exclusive((prev, next_), 'pn')
        cur_idx = self._tabbed_browser.currentIndex()
        assert cur_idx != -1

        def _to_close(i):
            """Helper method to check if a tab should be closed or not."""
            return not (i == cur_idx or
                        (prev and i < cur_idx) or
                        (next_ and i > cur_idx))

        # close as many tabs as we can
        first_tab = True
        pinned_tabs_cleanup = False
        for i, tab in enumerate(self._tabbed_browser.widgets()):
            if _to_close(i):
                if force or not tab.data.pinned:
                    self._tabbed_browser.close_tab(tab, new_undo=first_tab)
                    first_tab = False
                else:
                    pinned_tabs_cleanup = tab

        # Check to see if we would like to close any pinned tabs
        if pinned_tabs_cleanup:
            self._tabbed_browser.tab_close_prompt_if_pinned(
                pinned_tabs_cleanup,
                force,
                lambda: self.tab_only(
                    prev=prev, next_=next_, force=True),
                text="Are you sure you want to close pinned tabs?")