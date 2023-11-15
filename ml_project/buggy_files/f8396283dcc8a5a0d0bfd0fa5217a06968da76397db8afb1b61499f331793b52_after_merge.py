    def battery_level(self):
        if not os.listdir(self.sys_battery_path):
            return {
                "full_text": "",
                "cached_until": self.py3.time_in(self.cache_timeout)
            }

        self._refresh_battery_info()
        self._update_icon()
        self._update_ascii_bar()
        self._update_full_text()

        return self._build_response()