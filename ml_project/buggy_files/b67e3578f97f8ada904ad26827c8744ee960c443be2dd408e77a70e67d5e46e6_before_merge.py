    def mousePressEvent(self, event):
        self.clicked.emit(False)
        QLabel.mousePressEvent(self, event)