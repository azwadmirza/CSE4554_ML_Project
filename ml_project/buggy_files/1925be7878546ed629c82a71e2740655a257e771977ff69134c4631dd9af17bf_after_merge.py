    def set_focus(self, idx):
        if self.view:
            if idx is None or idx < 0:
                idx = 0
            elif idx >= len(self.view):
                idx = len(self.view) - 1
            self.focus = idx
        else:
            self.focus = None