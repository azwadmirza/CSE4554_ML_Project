    def selected(self) -> Optional[Gtk.TreeIter]:
        (model, tree_iter) = self.selection.get_selected()
        return tree_iter