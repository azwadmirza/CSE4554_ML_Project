    def sort_view(self, key="name", ascending=True):
        """Sort the model on a given column name"""
        try:
            sort_column = self.sort_columns[key]
        except KeyError:
            logger.error("Invalid column name '%s'", key)
            sort_column = COL_NAME
        self.modelsort.set_sort_column_id(
            sort_column,
            Gtk.SortType.ASCENDING if ascending else Gtk.SortType.DESCENDING,
        )