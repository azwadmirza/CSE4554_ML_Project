    def battery_level(self):

        self._refresh_battery_info()

        self._update_icon()
        self._update_ascii_bar()
        self._update_full_text()

        return self._build_response()