    def keyPressEvent(self, event):
        """Reimplement Qt Method - Basic keypress event handler"""
        event, text, key, ctrl, shift = restore_keyevent(event)
        if key == Qt.Key_Question and not self.has_selected_text():
            self._key_question(text, force=True)
        elif key == Qt.Key_ParenLeft and not self.has_selected_text() \
          and self.help_enabled:
            self._key_question(text)
        else:
            # Let the parent widget handle the key press event
            QTextEdit.keyPressEvent(self, event)