    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.setStyleSheet("background-color: rgba(30, 30, 30, 0.75);")

        self.dialog_widget = QWidget(self)

        connect(self.window().resize_event, self.on_main_window_resize)