    def clear(self):
        marked_flows = [f for f in self.state.view if f.marked]
        super(ConsoleState, self).clear()

        for f in marked_flows:
            self.add_flow(f)
            f.marked = True

        if len(self.flows.views) == 0:
            self.focus = None
        else:
            self.focus = 0
        self.set_focus(self.focus)