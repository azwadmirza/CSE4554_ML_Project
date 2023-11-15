    def tabopen(self, url=None, background=None, related=True, idx=None, *,
                ignore_tabs_are_windows=False):
        """Open a new tab with a given URL.

        Inner logic for open-tab and open-tab-bg.
        Also connect all the signals we need to _filter_signals.

        Args:
            url: The URL to open as QUrl or None for an empty tab.
            background: Whether to open the tab in the background.
                        if None, the `tabs.background_tabs`` setting decides.
            related: Whether the tab was opened from another existing tab.
                     If this is set, the new position might be different. With
                     the default settings we handle it like Chromium does:
                         - Tabs from clicked links etc. are to the right of
                           the current (related=True).
                         - Explicitly opened tabs are at the very right
                           (related=False)
            idx: The index where the new tab should be opened.
            ignore_tabs_are_windows: If given, never open a new window, even
                                     with tabs.tabs_are_windows set.

        Return:
            The opened WebView instance.
        """
        if url is not None:
            qtutils.ensure_valid(url)
        log.webview.debug("Creating new tab with URL {}, background {}, "
                          "related {}, idx {}".format(
                              url, background, related, idx))

        if (config.val.tabs.tabs_are_windows and self.widget.count() > 0 and
                not ignore_tabs_are_windows):
            window = mainwindow.MainWindow(private=self.private)
            window.show()
            tabbed_browser = objreg.get('tabbed-browser', scope='window',
                                        window=window.win_id)
            return tabbed_browser.tabopen(url=url, background=background,
                                          related=related)

        tab = browsertab.create(win_id=self._win_id, private=self.private,
                                parent=self.widget)
        self._connect_tab_signals(tab)

        if idx is None:
            idx = self._get_new_tab_idx(related)
        self.widget.insertTab(idx, tab, "")

        if url is not None:
            tab.openurl(url)

        if background is None:
            background = config.val.tabs.background
        if background:
            # Make sure the background tab has the correct initial size.
            # With a foreground tab, it's going to be resized correctly by the
            # layout anyways.
            tab.resize(self.widget.currentWidget().size())
            self.widget.tab_index_changed.emit(self.widget.currentIndex(),
                                               self.widget.count())
        else:
            self.widget.setCurrentWidget(tab)

        tab.show()
        self.new_tab.emit(tab, idx)
        return tab