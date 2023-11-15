    def _on_key_pressed(self, event):
        if event.isAccepted():
            return

        with QMutexLocker(self.event_lock):
            key = event.key()
            text = to_text_string(event.text())

            if self.is_snippet_active:
                line, column = self.editor.get_cursor_line_column()
                node, snippet, text_node = self._find_node_by_position(
                    line, column)
                if key == Qt.Key_Tab:
                    event.accept()
                    next_snippet = ((self.active_snippet + 1) %
                                    len(self.snippets_map))
                    self.select_snippet(next_snippet)

                    if next_snippet == 0:
                        self.reset()
                elif key == Qt.Key_Escape:
                    self.reset()
                    event.accept()
                elif len(text) > 0:
                    not_brace = text not in {'(', ')', '[', ']', '{', '}'}
                    not_completion = (
                        text not in self.editor.auto_completion_characters)
                    not_signature = (
                        text not in self.editor.signature_completion_characters
                    )
                    valid = not_brace and not_completion and not_signature
                    if node is not None:
                        if snippet is None or text == '\n':
                            # Constant text identifier was modified
                            self.reset()
                        elif valid or text == '\b':
                            self._process_text(text)