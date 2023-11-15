    def mouseMoveEvent(self, event):
        position = np.array([event.pos().x(), event.pos().y()])
        distance = np.linalg.norm(position - self.drag_start_position)
        if (
            distance < QApplication.startDragDistance()
            or self.drag_name is None
        ):
            return
        mimeData = QMimeData()
        mimeData.setText(self.drag_name)
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(event.pos() - self.rect().topLeft())
        dropAction = drag.exec_()