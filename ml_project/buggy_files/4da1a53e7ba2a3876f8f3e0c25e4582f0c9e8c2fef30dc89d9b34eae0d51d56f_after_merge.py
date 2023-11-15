    def keyPressEvent(self, event):
        text, key = event.text(), event.key()
        alt = event.modifiers() & Qt.AltModifier
        shift = event.modifiers() & Qt.ShiftModifier
        ctrl = event.modifiers() & Qt.ControlModifier
        modifier = shift or ctrl or alt
        if key in (Qt.Key_Return, Qt.Key_Enter) or key == Qt.Key_Tab:
            self.item_selected()
        elif key == Qt.Key_Escape:
            self.hide()
        elif key in (Qt.Key_Return, Qt.Key_Enter,
                     Qt.Key_Left, Qt.Key_Right) or text in ('.', ':'):
            self.hide()
            self.textedit.keyPressEvent(event)
        elif key in (Qt.Key_Up, Qt.Key_Down, Qt.Key_PageUp, Qt.Key_PageDown,
                     Qt.Key_Home, Qt.Key_End,
                     Qt.Key_CapsLock) and not modifier:
            if key == Qt.Key_Up and self.currentRow() == 0:
                self.setCurrentRow(self.count() - 1)
            elif key == Qt.Key_Down and self.currentRow() == self.count()-1:
                self.setCurrentRow(0)
            else:
                QListWidget.keyPressEvent(self, event)
        elif len(text) or key == Qt.Key_Backspace:
            # If the cursor goes behind the current position,
            # the autocomplete is no longer relevant
            if self.textedit.textCursor().position() < self.position or (
                    key == Qt.Key_Backspace and (
                    self.textedit.textCursor().position() <= self.position)):
                self.hide()
                self.textedit.keyPressEvent(event)
            else:
                self.textedit.keyPressEvent(event)
                self.update_current()
        elif modifier:
            self.textedit.keyPressEvent(event)
        else:
            self.hide()
            QListWidget.keyPressEvent(self, event)