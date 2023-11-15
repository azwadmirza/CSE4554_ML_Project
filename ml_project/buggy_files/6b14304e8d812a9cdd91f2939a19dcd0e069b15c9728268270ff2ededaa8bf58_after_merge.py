    def mouseMoveEvent(self, event):
        """Drag and drop layer with mouse movement.

        Parameters
        ----------
        event : qtpy.QtCore.QEvent
            Event from the Qt context.
        """
        position = np.array([event.pos().x(), event.pos().y()])
        distance = np.linalg.norm(position - self._drag_start_position)
        if (
            distance < QApplication.startDragDistance()
            or self._drag_name is None
        ):
            return
        mimeData = QMimeData()
        mimeData.setText(self._drag_name)
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(event.pos() - self.rect().topLeft())
        drag.exec_()
        # Check if dragged layer still exists or was deleted during drag
        names = [layer.name for layer in self.layers]
        dragged_layer_exists = self._drag_name in names
        if self._drag_name is not None and dragged_layer_exists:
            index = self.layers.index(self._drag_name)
            layer = self.layers[index]
            self._ensure_visible(layer)