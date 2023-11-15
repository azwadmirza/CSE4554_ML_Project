    def mouseMoveEvent(self, event):
        """Underline words when pressing <CONTROL>"""
        self.mouse_point = event.pos()
        QToolTip.hideText()
        if event.modifiers() & Qt.AltModifier:
            self.sig_alt_mouse_moved.emit(event)
            event.accept()
            return

        if self.has_selected_text():
            TextEditBaseWidget.mouseMoveEvent(self, event)
            return
        if self.go_to_definition_enabled and \
           event.modifiers() & Qt.ControlModifier:
            text = self.get_word_at(event.pos())
            if (text and not sourcecode.is_keyword(to_text_string(text))):
                if not self.__cursor_changed:
                    QApplication.setOverrideCursor(
                                                QCursor(Qt.PointingHandCursor))
                    self.__cursor_changed = True
                cursor = self.cursorForPosition(event.pos())
                cursor.select(QTextCursor.WordUnderCursor)
                self.clear_extra_selections('ctrl_click')
                self.__highlight_selection(
                    'ctrl_click', cursor, update=True,
                    foreground_color=self.ctrl_click_color,
                    underline_color=self.ctrl_click_color,
                    underline_style=QTextCharFormat.SingleUnderline)
                event.accept()
                return
        if self.__cursor_changed:
            QApplication.restoreOverrideCursor()
            self.__cursor_changed = False
            self.clear_extra_selections('ctrl_click')
        # TODO: LSP addition - Define hover expected behaviour and UI element
        # else:
        #     cursor = self.cursorForPosition(event.pos())
        #     line, col = cursor.blockNumber(), cursor.columnNumber()
        #     if self.enable_hover:
        #         self.request_hover(line, col)
        TextEditBaseWidget.mouseMoveEvent(self, event)