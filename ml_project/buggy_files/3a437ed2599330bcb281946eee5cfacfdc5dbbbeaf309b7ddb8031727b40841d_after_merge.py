    def accept(self):
        """Reimplement Qt method."""
        try:
            for index in range(self.stack.count()):
                self.stack.widget(index).accept_changes()
            QDialog.accept(self)
        except RuntimeError:
            # Sometimes under CI testing the object the following error appears
            # RuntimeError: wrapped C/C++ object has been deleted
            pass