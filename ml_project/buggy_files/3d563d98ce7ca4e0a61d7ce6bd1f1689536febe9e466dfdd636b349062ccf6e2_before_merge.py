    def add_flow(self, f):
        super(ConsoleState, self).add_flow(f)
        if self.focus is None:
            self.set_focus(0)
        elif self.follow_focus:
            self.set_focus(len(self.view) - 1)
        self.set_flow_marked(f, False)
        return f