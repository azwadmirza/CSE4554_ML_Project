    def on_choice(self, event):
        self.data.name = self.chooser.GetStringSelection()
        self.show_check.SetValue(True)
        self.workspace_view.redraw()