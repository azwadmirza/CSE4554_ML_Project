    def _emit_changed(self):
        """
        A context manager that calls `emit_selection_rows_changed after
        changing a selection.
        """
        def map_from_source(rows):
            from_src = self.proxy.mapFromSource
            index = self.proxy.sourceModel().index
            return {from_src(index(row, 0)).row() for row in rows}

        old_rows = self._rows.copy()
        try:
            yield
        finally:
            if self.proxy.sourceModel() is not None:
                deselected = map_from_source(old_rows - self._rows)
                selected = map_from_source(self._rows - old_rows)
                if selected or deselected:
                    for model in self._selection_models:
                        model.emit_selection_rows_changed(selected, deselected)