    def show(self):
        """Overrides Qt Method"""
        QWidget.show(self)
        self.visibility_changed.emit(True)
        if self.editor is not None:
            text = self.editor.get_selected_text()

            # If no text is highlighted for search, use whatever word is under
            # the cursor
            if not text:
                try:
                    cursor = self.editor.textCursor()
                    cursor.select(QTextCursor.WordUnderCursor)
                    text = to_text_string(cursor.selectedText())
                except AttributeError:
                    # We can't do this for all widgets, e.g. WebView's
                    pass

            # Now that text value is sorted out, use it for the search
            if text:
                self.search_text.setEditText(text)
                self.search_text.lineEdit().selectAll()
                self.refresh()
            else:
                self.search_text.lineEdit().selectAll()
            self.search_text.setFocus()