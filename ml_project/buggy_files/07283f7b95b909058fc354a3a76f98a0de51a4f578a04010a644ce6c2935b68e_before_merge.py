    def _on_config_changed(self, option):
        if option == 'tabs.favicons.show':
            self._update_favicons()
        elif option == 'window.title_format':
            self._update_window_title()
        elif option in ['tabs.title.format', 'tabs.title.format_pinned']:
            self._update_tab_titles()