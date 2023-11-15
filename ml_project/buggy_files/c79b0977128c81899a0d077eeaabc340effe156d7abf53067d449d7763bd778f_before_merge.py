    def on_selection_change(self, selection, action=SomView.SelectionSet):
        if self.selection is None:
            self.selection = np.zeros(self.grid_cells.T.shape, dtype=np.int16)
        if action == SomView.SelectionSet:
            self.selection[:] = 0
            self.selection[selection] = 1
        elif action == SomView.SelectionAddToGroup:
            self.selection[selection] = max(1, np.max(self.selection))
        elif action == SomView.SelectionNewGroup:
            self.selection[selection] = 1 + np.max(self.selection)
        elif action & SomView.SelectionRemove:
            self.selection[selection] = 0
        self.redraw_selection()
        self.update_output()