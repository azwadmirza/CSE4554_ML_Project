    def handle_new_screen(self, screen):
        """Connect DPI signals for new screen."""
        self.screen.logicalDotsPerInchChanged.disconnect(
            self.show_dpi_change_message)
        self.screen = screen
        self.screen.logicalDotsPerInchChanged.connect(
            self.show_dpi_change_message)