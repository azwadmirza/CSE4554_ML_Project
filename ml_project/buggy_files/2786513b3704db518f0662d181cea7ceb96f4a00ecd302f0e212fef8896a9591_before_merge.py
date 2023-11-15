    def item_focus(self, which):
        # This duplicates some completion code, but I don't see a nicer way...
        assert which in ['prev', 'next'], which
        selmodel = self._file_view.selectionModel()

        parent = self._file_view.rootIndex()
        first_index = self._file_model.index(0, 0, parent)
        row = self._file_model.rowCount(parent) - 1
        last_index = self._file_model.index(row, 0, parent)

        if not first_index.isValid():
            # No entries
            return

        assert last_index.isValid()

        idx = selmodel.currentIndex()
        if not idx.isValid():
            # No item selected yet
            idx = last_index if which == 'prev' else first_index
        elif which == 'prev':
            idx = self._file_view.indexAbove(idx)
        else:
            assert which == 'next', which
            idx = self._file_view.indexBelow(idx)

        # wrap around if we arrived at beginning/end
        if not idx.isValid():
            idx = last_index if which == 'prev' else first_index

        selmodel.setCurrentIndex(
            idx, QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)
        self._insert_path(idx, clicked=False)