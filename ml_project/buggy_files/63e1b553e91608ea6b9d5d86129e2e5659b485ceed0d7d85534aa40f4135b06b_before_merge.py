    def backlight(self):
        level = self._get_backlight_level()
        full_text = self.py3.safe_format(self.format, {'level': level})
        response = {
            'cached_until': self.py3.time_in(self.cache_timeout),
            'full_text': full_text
        }
        return response