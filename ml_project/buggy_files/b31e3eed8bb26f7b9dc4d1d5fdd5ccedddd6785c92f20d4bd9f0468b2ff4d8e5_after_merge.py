    def toggle_selection(self):
        self.selection_enabled = not self.selection_enabled
        self.selection_toggled.emit(self.selection_enabled)