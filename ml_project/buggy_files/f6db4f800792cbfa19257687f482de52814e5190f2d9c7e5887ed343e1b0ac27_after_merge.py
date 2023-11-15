    def handle_new_screen(self, screen):
        """Connect DPI signals for new screen."""
        try:
            self.screen.logicalDotsPerInchChanged.disconnect(
                self.show_dpi_change_message)
        except (TypeError, RuntimeError):
            # See spyder-ide/spyder#11903 and spyder-ide/spyder#11997
            pass
        self.screen = screen
        self.screen.logicalDotsPerInchChanged.connect(
            self.show_dpi_change_message)