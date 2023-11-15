    def _update_favicons(self):
        """Update favicons when config was changed."""
        for i, tab in enumerate(self.widgets()):
            if config.val.tabs.favicons.show:
                self.setTabIcon(i, tab.icon())
                if config.val.tabs.tabs_are_windows:
                    self.window().setWindowIcon(tab.icon())
            else:
                self.setTabIcon(i, QIcon())
                if config.val.tabs.tabs_are_windows:
                    self.window().setWindowIcon(self.default_window_icon)