    def mousePressEvent(self, event):
        self.clicked.emit()
        QLabel.mousePressEvent(self, event)