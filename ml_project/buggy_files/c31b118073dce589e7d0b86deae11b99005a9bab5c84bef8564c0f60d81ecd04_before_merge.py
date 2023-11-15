    def dragEnterEvent(self, event):
        divs = []
        for i in range(0, self.vbox_layout.count(), 2):
            widget = self.vbox_layout.itemAt(i).widget()
            divs.append(widget.y() + widget.frameGeometry().height() / 2)
        self.centers = [
            (divs[i + 1] + divs[i]) / 2 for i in range(len(divs) - 1)
        ]
        event.accept()