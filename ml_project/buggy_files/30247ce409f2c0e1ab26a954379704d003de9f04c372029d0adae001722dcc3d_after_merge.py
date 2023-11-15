    def undo(self):
        """Undo removing of a tab or tabs."""
        # Remove unused tab which may be created after the last tab is closed
        last_close = config.val.tabs.last_close
        use_current_tab = False
        if last_close in ['blank', 'startpage', 'default-page']:
            only_one_tab_open = self.widget.count() == 1
            no_history = len(self.widget.widget(0).history) == 1
            urls = {
                'blank': QUrl('about:blank'),
                'startpage': config.val.url.start_pages[0],
                'default-page': config.val.url.default_page,
            }
            first_tab_url = self.widget.widget(0).url()
            last_close_urlstr = urls[last_close].toString().rstrip('/')
            first_tab_urlstr = first_tab_url.toString().rstrip('/')
            last_close_url_used = first_tab_urlstr == last_close_urlstr
            use_current_tab = (only_one_tab_open and no_history and
                               last_close_url_used)

        for entry in reversed(self._undo_stack.pop()):
            if use_current_tab:
                newtab = self.widget.widget(0)
                use_current_tab = False
            else:
                newtab = self.tabopen(background=False, idx=entry.index)

            newtab.history.deserialize(entry.history)
            self.widget.set_tab_pinned(newtab, entry.pinned)