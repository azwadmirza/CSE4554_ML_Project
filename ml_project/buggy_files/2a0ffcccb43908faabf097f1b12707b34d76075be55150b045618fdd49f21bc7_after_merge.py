    def compare(self, iter_a: Optional[Gtk.TreeIter], iter_b: Optional[Gtk.TreeIter]) -> bool:
        if iter_a is not None and iter_b is not None:
            model = self.get_model()
            assert model is not None
            return model.get_path(iter_a) == model.get_path(iter_b)
        else:
            return False