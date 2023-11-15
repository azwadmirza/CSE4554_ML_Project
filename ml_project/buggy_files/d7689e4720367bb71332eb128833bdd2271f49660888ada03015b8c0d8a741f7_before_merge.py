    def _add_widgets(self):
        """Add or readd all widgets to the VBox."""
        self._vbox.removeWidget(self.tabbed_browser)
        self._vbox.removeWidget(self._downloadview)
        self._vbox.removeWidget(self.status)
        widgets = [self.tabbed_browser]

        downloads_position = config.val.downloads.position
        if downloads_position == 'top':
            widgets.insert(0, self._downloadview)
        elif downloads_position == 'bottom':
            widgets.append(self._downloadview)
        else:
            raise ValueError("Invalid position {}!".format(downloads_position))

        status_position = config.val.statusbar.position
        if status_position == 'top':
            widgets.insert(0, self.status)
        elif status_position == 'bottom':
            widgets.append(self.status)
        else:
            raise ValueError("Invalid position {}!".format(status_position))

        for widget in widgets:
            self._vbox.addWidget(widget)