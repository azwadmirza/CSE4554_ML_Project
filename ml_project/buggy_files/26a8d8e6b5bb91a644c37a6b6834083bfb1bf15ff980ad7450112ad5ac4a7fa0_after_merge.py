    def winforms_item_selection_changed(self, sender, e):
        # update selection interface property
        self.interface._selection = self._selected_rows()

        if e.IsSelected and self.interface.on_select:
            self.interface.on_select(self.interface, row=self.interface.data[e.ItemIndex])