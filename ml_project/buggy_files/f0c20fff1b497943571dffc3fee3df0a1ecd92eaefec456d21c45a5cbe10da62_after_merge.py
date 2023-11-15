    def _on_config_changed(self, option: str):
        if option == 'fonts.tabs':
            self._set_font()
        elif option == 'tabs.favicons.scale':
            self._set_icon_size()
        elif option == 'colors.tabs.bar.bg':
            self._set_colors()
        elif option == 'tabs.show_switching_delay':
            self._on_show_switching_delay_changed()
        elif option == 'tabs.show':
            self.maybe_hide()

        if option.startswith('colors.tabs.'):
            self.update()

        # Clear _minimum_tab_size_hint_helper cache when appropriate
        if option in ["tabs.indicator.padding",
                      "tabs.padding",
                      "tabs.indicator.width",
                      "tabs.min_width",
                      "tabs.pinned.shrink"]:
            self._minimum_tab_size_hint_helper.cache_clear()