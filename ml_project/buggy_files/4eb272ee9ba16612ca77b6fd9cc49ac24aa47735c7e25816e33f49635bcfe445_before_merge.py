    def clicked_menu_button_debug(self, index):
        if not self.debug_window:
            self.debug_window = DebugWindow(self.tribler_settings, self.tribler_version)
        self.debug_window.show()