    def _on_mode_entered(self, mode):
        if mode != usertypes.KeyMode.caret:
            return

        if self._tab.search.search_displayed:
            # We are currently in search mode.
            # convert the search to a blue selection so we can operate on it
            # https://bugreports.qt.io/browse/QTBUG-60673
            self._tab.search.clear()

        self._tab.run_js_async(
            javascript.assemble('caret', 'setPlatform', sys.platform))
        self._js_call('setInitialCursor')