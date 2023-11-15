    def keypress(self, size, key):
        key = common.shortcuts(key)
        if key == "z":
            self.master.clear_events()
            key = None
        elif key == "G":
            self.set_focus(len(self.master.logbuffer) - 1)
        elif key == "g":
            self.set_focus(0)
        elif key == "F":
            o = self.master.options
            o.console_focus_follow = not o.console_focus_follow
        return urwid.ListBox.keypress(self, size, key)