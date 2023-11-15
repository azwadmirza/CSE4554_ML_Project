    def on_current_changed(self, idx):
        """Set last-focused-tab and leave hinting mode when focus changed."""
        mode_on_change = config.val.tabs.mode_on_change
        modes_to_save = [usertypes.KeyMode.insert,
                         usertypes.KeyMode.passthrough]
        if idx == -1 or self.shutting_down:
            # closing the last tab (before quitting) or shutting down
            return
        tab = self.widget(idx)
        if tab is None:
            log.webview.debug("on_current_changed got called with invalid "
                              "index {}".format(idx))
            return
        if self._now_focused is not None and mode_on_change == 'restore':
            current_mode = modeman.instance(self._win_id).mode
            if current_mode not in modes_to_save:
                current_mode = usertypes.KeyMode.normal
            self._now_focused.data.input_mode = current_mode

        log.modes.debug("Current tab changed, focusing {!r}".format(tab))
        tab.setFocus()

        modes_to_leave = [usertypes.KeyMode.hint, usertypes.KeyMode.caret]
        if mode_on_change != 'persist':
            modes_to_leave += modes_to_save
        for mode in modes_to_leave:
            modeman.leave(self._win_id, mode, 'tab changed', maybe=True)
        if mode_on_change == 'restore':
            modeman.enter(self._win_id, tab.data.input_mode,
                          'restore input mode for tab')
        if self._now_focused is not None:
            objreg.register('last-focused-tab', self._now_focused, update=True,
                            scope='window', window=self._win_id)
        self._now_focused = tab
        self.current_tab_changed.emit(tab)
        QTimer.singleShot(0, self._update_window_title)
        self._tab_insert_idx_left = self.currentIndex()
        self._tab_insert_idx_right = self.currentIndex() + 1