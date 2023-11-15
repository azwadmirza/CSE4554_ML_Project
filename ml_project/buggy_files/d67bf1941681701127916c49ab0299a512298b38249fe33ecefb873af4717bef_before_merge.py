    def _update_window_title(self, field=None):
        """Change the window title to match the current tab.

        Args:
            idx: The tab index to update.
            field: A field name which was updated. If given, the title
                   is only set if the given field is in the template.
        """
        title_format = config.val.window.title_format
        if field is not None and ('{' + field + '}') not in title_format:
            return

        idx = self.currentIndex()
        if idx == -1:
            # (e.g. last tab removed)
            log.webview.debug("Not updating window title because index is -1")
            return
        fields = self.get_tab_fields(idx)
        fields['id'] = self._win_id

        title = title_format.format(**fields)
        self.window().setWindowTitle(title)