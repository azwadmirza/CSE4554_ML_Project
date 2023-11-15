    def _on_config_changed(self, option):
        """Resize the completion if related config options changed."""
        if option == 'statusbar.padding':
            self._update_overlay_geometries()
        elif option == 'downloads.position':
            self._add_widgets()
        elif option == 'statusbar.position':
            self._add_widgets()
            self._update_overlay_geometries()