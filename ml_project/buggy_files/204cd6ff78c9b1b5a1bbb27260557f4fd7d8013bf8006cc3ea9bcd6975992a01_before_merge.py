    def selected(self) -> Gtk.TreeIter:
        (model, tree_iter) = self.selection.get_selected()
        assert tree_iter is not None
        return tree_iter