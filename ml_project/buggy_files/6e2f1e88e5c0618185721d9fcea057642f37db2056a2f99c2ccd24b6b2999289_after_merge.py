    def cmd_change_backlight(self, direction):
        if self._future and not self._future.done():
            return
        new = now = self._get_info() * 100
        if direction is ChangeDirection.DOWN:
            new = max(now - self.step, 0)
        elif direction is ChangeDirection.UP:
            new = min(now + self.step, 100)
        if new != now:
            self._future = self.qtile.run_in_executor(self._change_backlight, new)