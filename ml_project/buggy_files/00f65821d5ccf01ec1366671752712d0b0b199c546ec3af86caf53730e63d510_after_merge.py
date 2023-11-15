    def on_scroll_pos_changed(self):
        """Update tab and window title when scroll position changed."""
        idx = self.widget.currentIndex()
        if idx == -1:
            # (e.g. last tab removed)
            log.webview.debug("Not updating scroll position because index is "
                              "-1")
            return
        self._update_window_title('scroll_pos')
        self.widget.update_tab_title(idx, 'scroll_pos')