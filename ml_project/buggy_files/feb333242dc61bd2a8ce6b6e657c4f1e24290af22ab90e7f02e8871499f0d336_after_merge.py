    def _on_key_pressed(self, event):
        """
        Override key press to select the current scope if the user wants
        to deleted a folded scope (without selecting it).
        """
        delete_request = event.key() in {Qt.Key_Delete, Qt.Key_Backspace}
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            if event.key() == Qt.Key_Return:
                delete_request = True

        if event.text() or delete_request:
            self._key_pressed = True
            if cursor.hasSelection():
                # change selection to encompass the whole scope.
                positions_to_check = cursor.selectionStart(), cursor.selectionEnd()
            else:
                positions_to_check = (cursor.position(), )
            for pos in positions_to_check:
                block = self.editor.document().findBlock(pos)
                start_line = block.blockNumber() + 2
                if (start_line in self.folding_regions and
                        self.folding_status[start_line]):
                    end_line = self.folding_regions[start_line]
                    if delete_request and cursor.hasSelection():
                        tc = TextHelper(self.editor).select_lines(start_line, end_line)
                        if tc.selectionStart() > cursor.selectionStart():
                            start = cursor.selectionStart()
                        else:
                            start = tc.selectionStart()
                        if tc.selectionEnd() < cursor.selectionEnd():
                            end = cursor.selectionEnd()
                        else:
                            end = tc.selectionEnd()
                        tc.setPosition(start)
                        tc.setPosition(end, tc.KeepAnchor)
                        self.editor.setTextCursor(tc)
            self._key_pressed = False