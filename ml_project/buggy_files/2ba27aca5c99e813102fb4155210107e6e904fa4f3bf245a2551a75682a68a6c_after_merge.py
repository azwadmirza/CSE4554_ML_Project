    def toggle_selection(self):
        self._js_call('toggleSelection', self.selection_toggled.emit)