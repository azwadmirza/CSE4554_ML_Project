    def __init__(self, **config):
        base.InLoopPollText.__init__(self, **config)
        self.add_defaults(Backlight.defaults)
        self._future = None

        self.brightness_file = os.path.join(
            BACKLIGHT_DIR, self.backlight_name, self.brightness_file,
        )
        self.max_brightness_file = os.path.join(
            BACKLIGHT_DIR, self.backlight_name, self.max_brightness_file,
        )

        mouse_callbacks = {
            'Button4': lambda q: self.cmd_change_backlight(ChangeDirection.UP),
            'Button5': lambda q: self.cmd_change_backlight(ChangeDirection.DOWN),
        }
        mouse_callbacks.update(self.mouse_callbacks)
        self.mouse_callbacks = mouse_callbacks