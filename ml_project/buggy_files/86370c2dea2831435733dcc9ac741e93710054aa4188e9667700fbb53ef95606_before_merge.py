    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyRelease and self.isVisible() and not self.window().top_search_bar.hasFocus() and\
                event.key() == Qt.Key_Space:
            self.on_play_pause_button_click()
        return QWidget.eventFilter(self, source, event)