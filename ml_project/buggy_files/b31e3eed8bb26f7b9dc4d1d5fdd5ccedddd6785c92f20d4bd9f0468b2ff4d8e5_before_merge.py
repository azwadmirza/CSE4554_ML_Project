    def toggle_selection(self):
        self.selection_enabled = not self.selection_enabled
        mainwindow = objreg.get('main-window', scope='window',
                                window=self._tab.win_id)
        mainwindow.status.set_mode_active(usertypes.KeyMode.caret, True)