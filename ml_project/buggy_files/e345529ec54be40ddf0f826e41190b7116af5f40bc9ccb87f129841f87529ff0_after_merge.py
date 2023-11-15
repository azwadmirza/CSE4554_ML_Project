    def contextMenuEvent(self, event):
        """Override Qt method"""
        # Needed to handle not initialized menu.
        # See issue 6975
        try:
            self.update_menu()
            self.menu.popup(event.globalPos())
        except AttributeError:
            pass