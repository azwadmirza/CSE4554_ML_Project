    def change_this_display_mode(self, t):
        view = contentviews.get_by_shortcut(t)
        if view:
            self.view.settings[self.flow][(self.tab_offset, "prettyview")] = view.name
        else:
            self.view.settings[self.flow][(self.tab_offset, "prettyview")] = None
        signals.flow_change.send(self, flow=self.flow)