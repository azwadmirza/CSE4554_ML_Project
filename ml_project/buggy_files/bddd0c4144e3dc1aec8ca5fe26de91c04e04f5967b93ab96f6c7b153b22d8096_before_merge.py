    def close_dialog(self, checked=False):
        try:
            self.setParent(None)
            self.deleteLater()
        except RuntimeError:
            pass