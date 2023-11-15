    def set_mode_active(self, mode, val):
        """Setter for self.{insert,command,caret}_active.

        Re-set the stylesheet after setting the value, so everything gets
        updated by Qt properly.
        """
        if mode == usertypes.KeyMode.insert:
            log.statusbar.debug("Setting insert flag to {}".format(val))
            self._color_flags.insert = val
        if mode == usertypes.KeyMode.passthrough:
            log.statusbar.debug("Setting passthrough flag to {}".format(val))
            self._color_flags.passthrough = val
        if mode == usertypes.KeyMode.command:
            log.statusbar.debug("Setting command flag to {}".format(val))
            self._color_flags.command = val
        elif mode in [usertypes.KeyMode.prompt, usertypes.KeyMode.yesno]:
            log.statusbar.debug("Setting prompt flag to {}".format(val))
            self._color_flags.prompt = val
        elif mode == usertypes.KeyMode.caret:
            tab = self._current_tab()
            log.statusbar.debug("Setting caret flag - val {}, selection "
                                "{}".format(val, tab.caret.selection_enabled))
            if val:
                if tab.caret.selection_enabled:
                    self._set_mode_text("{} selection".format(mode.name))
                    self._color_flags.caret = ColorFlags.CaretMode.selection
                else:
                    self._set_mode_text(mode.name)
                    self._color_flags.caret = ColorFlags.CaretMode.on
            else:
                self._color_flags.caret = ColorFlags.CaretMode.off
        config.set_register_stylesheet(self, update=False)