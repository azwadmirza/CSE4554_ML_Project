    def select(self, selection: Union[QModelIndex, QItemSelection], flags: int):
        """
        (De)Select given rows

        Args:
            selection (QModelIndex or QItemSelection):
                rows to select; indices refer to the proxy model, not the source
            flags (QItemSelectionModel.SelectionFlags):
                flags that tell whether to Clear, Select, Deselect or Toggle
        """
        if isinstance(selection, QModelIndex):
            if selection.model() is not None:
                rows = {selection.model().mapToSource(selection).row()}
            else:
                rows = set()
        else:
            indices = selection.indexes()
            if indices:
                selection = indices[0].model().mapSelectionToSource(selection)
                rows = {index.row() for index in selection.indexes()}
            else:
                rows = set()
        self.select_rows(rows, flags)