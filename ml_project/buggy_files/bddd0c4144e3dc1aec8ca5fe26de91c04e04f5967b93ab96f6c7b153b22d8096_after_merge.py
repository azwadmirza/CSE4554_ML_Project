    def close_dialog(self, checked=False):
        try:
            self.setParent(None)
            self.deleteLater()
            self.closed = True
        except RuntimeError:
            pass