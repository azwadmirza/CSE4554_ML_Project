    def on_choice(self, event):
        self.data.name = self.chooser.GetStringSelection()
        self.workspace_view.redraw()