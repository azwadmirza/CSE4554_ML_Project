    def cmd_change_backlight(self, direction):
        if self.future and not self.future.done():
            return
        info = self._get_info()
        if not info:
            new = now = self.max_value
        else:
            new = now = info["brightness"]
        if direction is ChangeDirection.DOWN:  # down
            new = max(now - self.step, 0)
        elif direction is ChangeDirection.UP:  # up
            new = min(now + self.step, self.max_value)
        if new != now:
            self.future = self.qtile.run_in_executor(self.change_backlight,
                                                     new)