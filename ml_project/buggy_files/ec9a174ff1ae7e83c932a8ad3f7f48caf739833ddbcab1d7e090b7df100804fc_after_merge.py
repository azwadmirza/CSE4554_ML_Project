    def focus_event(self):
        if self.focus is None:
            return None
        else:
            return self.focus.original_widget