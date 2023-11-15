    def sort_view(self, key="name", ascending=True):
        self.modelsort.set_sort_column_id(
            self.sort_columns[key],
            Gtk.SortType.ASCENDING if ascending else Gtk.SortType.DESCENDING,
        )