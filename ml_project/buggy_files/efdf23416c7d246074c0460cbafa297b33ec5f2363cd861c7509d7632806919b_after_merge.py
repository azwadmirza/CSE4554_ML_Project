    def _remove_tab(self, tab, *, add_undo=True, new_undo=True, crashed=False):
        """Remove a tab from the tab list and delete it properly.

        Args:
            tab: The QWebView to be closed.
            add_undo: Whether the tab close can be undone.
            new_undo: Whether the undo entry should be a new item in the stack.
            crashed: Whether we're closing a tab with crashed renderer process.
        """
        idx = self.widget.indexOf(tab)
        if idx == -1:
            if crashed:
                return
            raise TabDeletedError("tab {} is not contained in "
                                  "TabbedWidget!".format(tab))
        if tab is self._now_focused:
            self._now_focused = None
        if tab is objreg.get('last-focused-tab', None, scope='window',
                             window=self._win_id):
            objreg.delete('last-focused-tab', scope='window',
                          window=self._win_id)

        if tab.url().isEmpty():
            # There are some good reasons why a URL could be empty
            # (target="_blank" with a download, see [1]), so we silently ignore
            # this.
            # [1] https://github.com/qutebrowser/qutebrowser/issues/163
            pass
        elif not tab.url().isValid():
            # We display a warning for URLs which are not empty but invalid -
            # but we don't return here because we want the tab to close either
            # way.
            urlutils.invalid_url_error(tab.url(), "saving tab")
        elif add_undo:
            try:
                history_data = tab.history.serialize()
            except browsertab.WebTabError:
                pass  # special URL
            else:
                entry = UndoEntry(tab.url(), history_data, idx,
                                  tab.data.pinned)
                if new_undo or not self._undo_stack:
                    self._undo_stack.append([entry])
                else:
                    self._undo_stack[-1].append(entry)

        tab.shutdown()
        self.widget.removeTab(idx)
        if not crashed:
            # WORKAROUND for a segfault when we delete the crashed tab.
            # see https://bugreports.qt.io/browse/QTBUG-58698
            tab.layout().unwrap()
            tab.deleteLater()