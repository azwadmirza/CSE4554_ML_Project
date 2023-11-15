    def __init__(self, **config):
        base.InLoopPollText.__init__(self, **config)
        self.add_defaults(Backlight.defaults)
        self.future = None

        self.brightness_file = os.path.join(
            BACKLIGHT_DIR, self.backlight_name, self.brightness_file,
        )
        self.max_brightness_file = os.path.join(
            BACKLIGHT_DIR, self.backlight_name, self.max_brightness_file,
        )
        self.max_value = self._load_file(self.max_brightness_file)
        self.step = self.max_value * self.step / 100