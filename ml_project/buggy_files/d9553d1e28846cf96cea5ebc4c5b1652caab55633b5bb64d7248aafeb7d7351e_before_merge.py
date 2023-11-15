    def close_tab(self, tab, *, add_undo=True, new_undo=True):
        """Close a tab.

        Args:
            tab: The QWebView to be closed.
            add_undo: Whether the tab close can be undone.
            new_undo: Whether the undo entry should be a new item in the stack.
        """
        last_close = config.val.tabs.last_close
        count = self.count()

        if last_close == 'ignore' and count == 1:
            return

        self._remove_tab(tab, add_undo=add_undo, new_undo=new_undo)

        if count == 1:  # We just closed the last tab above.
            if last_close == 'close':
                self.close_window.emit()
            elif last_close == 'blank':
                self.openurl(QUrl('about:blank'), newtab=True)
            elif last_close == 'startpage':
                for url in config.val.url.start_pages:
                    self.openurl(url, newtab=True)
            elif last_close == 'default-page':
                self.openurl(config.val.url.default_page, newtab=True)