    def hideEvent(self, event):
        """Reimplement Qt method"""
        for plugin in self.widgetlist:
            if plugin.isAncestorOf(self.last_focused_widget):
                plugin.visibility_changed(True)
        QMainWindow.hideEvent(self, event)