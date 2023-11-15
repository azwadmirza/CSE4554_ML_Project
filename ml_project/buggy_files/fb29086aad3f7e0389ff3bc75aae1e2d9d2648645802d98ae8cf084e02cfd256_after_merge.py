    def hideEvent(self, event):
        """Reimplement Qt method"""
        try:
            for plugin in self.widgetlist:
                if plugin.isAncestorOf(self.last_focused_widget):
                    plugin.visibility_changed(True)
            QMainWindow.hideEvent(self, event)
        except RuntimeError:
            QMainWindow.hideEvent(self, event)