    def on_tab_close_requested(self, idx):
        """Close a tab via an index."""
        tab = self.widget.widget(idx)
        if tab is None:
            log.webview.debug("Got invalid tab {} for index {}!".format(
                tab, idx))
            return
        self.tab_close_prompt_if_pinned(
            tab, False, lambda: self.close_tab(tab))