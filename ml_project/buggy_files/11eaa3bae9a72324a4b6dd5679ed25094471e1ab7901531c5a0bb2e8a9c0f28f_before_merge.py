    def load_items(self, items):
        stream, _data, cur_data = tabhistory.serialize(items)
        qtutils.deserialize_stream(stream, self._history)

        @pyqtSlot()
        def _on_load_finished():
            self._tab.scroller.to_point(cur_data['scroll-pos'])
            self._tab.load_finished.disconnect(_on_load_finished)

        if cur_data is not None:
            if 'zoom' in cur_data:
                self._tab.zoom.set_factor(cur_data['zoom'])
            if ('scroll-pos' in cur_data and
                    self._tab.scroller.pos_px() == QPoint(0, 0)):
                self._tab.load_finished.connect(_on_load_finished)