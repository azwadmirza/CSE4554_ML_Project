    def tab_clone(self, bg=False, window=False):
        """Duplicate the current tab.

        Args:
            bg: Open in a background tab.
            window: Open in a new window.

        Return:
            The new QWebView.
        """
        cmdutils.check_exclusive((bg, window), 'bw')
        curtab = self._current_widget()
        cur_title = self._tabbed_browser.page_title(self._current_index())
        try:
            history = curtab.history.serialize()
        except browsertab.WebTabError as e:
            raise cmdexc.CommandError(e)

        # The new tab could be in a new tabbed_browser (e.g. because of
        # tabs.tabs_are_windows being set)
        if window:
            new_tabbed_browser = self._new_tabbed_browser(
                private=self._tabbed_browser.private)
        else:
            new_tabbed_browser = self._tabbed_browser
        newtab = new_tabbed_browser.tabopen(background=bg)
        new_tabbed_browser = objreg.get('tabbed-browser', scope='window',
                                        window=newtab.win_id)
        idx = new_tabbed_browser.indexOf(newtab)

        new_tabbed_browser.set_page_title(idx, cur_title)
        if config.val.tabs.favicons.show:
            new_tabbed_browser.setTabIcon(idx, curtab.icon())
            if config.val.tabs.tabs_are_windows:
                new_tabbed_browser.window().setWindowIcon(curtab.icon())

        newtab.data.keep_icon = True
        newtab.history.deserialize(history)
        newtab.zoom.set_factor(curtab.zoom.factor())
        new_tabbed_browser.set_tab_pinned(newtab, curtab.data.pinned)
        return newtab