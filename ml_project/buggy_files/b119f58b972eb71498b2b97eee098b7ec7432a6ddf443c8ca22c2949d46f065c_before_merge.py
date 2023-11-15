    def _get_info(self):
        brightness = self._load_file(self.brightness_file)

        info = {
            'brightness': brightness,
            'max': self.max_value,
        }
        return info