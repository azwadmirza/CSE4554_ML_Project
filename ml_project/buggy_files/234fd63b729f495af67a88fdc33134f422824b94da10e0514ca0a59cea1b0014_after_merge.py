    def on_mode_left(self, mode):
        """Give focus to current tab if command mode was left."""
        if mode in [usertypes.KeyMode.command, usertypes.KeyMode.prompt,
                    usertypes.KeyMode.yesno]:
            widget = self.widget.currentWidget()
            log.modes.debug("Left status-input mode, focusing {!r}".format(
                widget))
            if widget is None:
                return
            widget.setFocus()