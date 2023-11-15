    def on_tab_cur_url_changed(self, tabs):
        """Called on URL changes."""
        tab = tabs.widget.currentWidget()
        if tab is None:  # pragma: no cover
            self.setText('')
            self.hide()
            return
        self.on_tab_changed(tab)