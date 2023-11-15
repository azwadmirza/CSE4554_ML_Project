    def insert_completion(self, completion, completion_position):
        """Insert a completion into the editor.

        completion_position is where the completion was generated.

        The replacement range is computed using the (LSP) completion's
        textEdit field if it exists. Otherwise, we replace from the
        start of the word under the cursor.
        """
        if not completion:
            return

        cursor = self.textCursor()

        has_selected_text = self.has_selected_text()
        selection_start, selection_end = self.get_selection_start_end()

        if isinstance(completion, dict) and 'textEdit' in completion:
            cursor.setPosition(completion['textEdit']['range']['start'])
            cursor.setPosition(completion['textEdit']['range']['end'],
                               QTextCursor.KeepAnchor)
            text = to_text_string(completion['textEdit']['newText'])
        else:
            text = completion
            if isinstance(completion, dict):
                text = completion['insertText']
            text = to_text_string(text)

            # Get word on the left of the cursor.
            result = self.get_current_word_and_position(completion=True)
            if result is not None:
                current_text, start_position = result
                end_position = start_position + len(current_text)
                # Check if the completion position is in the expected range
                if not start_position <= completion_position <= end_position:
                    return
                cursor.setPosition(start_position)
                # Remove the word under the cursor
                cursor.setPosition(end_position,
                                   QTextCursor.KeepAnchor)
            else:
                # Check if we are in the correct position
                if cursor.position() != completion_position:
                    return

        if has_selected_text:
            self.sig_will_remove_selection.emit(selection_start, selection_end)

        cursor.removeSelectedText()
        self.setTextCursor(cursor)

        # Add text
        if self.objectName() == 'console':
            # Handle completions for the internal console
            self.insert_text(text)
        else:
            if self.code_snippets:
                self.sig_insert_completion.emit(text)
            else:
                self.insert_text(text)
            self.document_did_change()