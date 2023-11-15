    def change_this_display_mode(self, t):
        name = contentviews.get_by_shortcut(t).name
        self.view.settings[self.flow][(self.tab_offset, "prettyview")] = name
        signals.flow_change.send(self, flow = self.flow)