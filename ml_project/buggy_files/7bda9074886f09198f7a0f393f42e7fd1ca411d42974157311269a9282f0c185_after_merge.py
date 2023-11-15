    def update_flow(self, f):
        super(ConsoleState, self).update_flow(f)
        if self.focus is None:
            self.set_focus(0)
        elif self.follow_focus:
            self.set_focus(self.flow_count())
        return f