    def on_selection_changed(self, _selection: Gtk.TreeSelection) -> None:
        tree_iter = self.List.selected()
        assert tree_iter
        if self.List.get_cursor()[0]:
            # GtkTreePath returns row when used as string
            self.Config["services-last-item"] = int(str(self.List.get_cursor()[0]))
        row = self.List.get(tree_iter, "id")
        rowid = row["id"]

        self.set_page(rowid)