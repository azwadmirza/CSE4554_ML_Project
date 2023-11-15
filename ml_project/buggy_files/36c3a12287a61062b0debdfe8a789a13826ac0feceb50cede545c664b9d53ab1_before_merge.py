    def create_shortcuts(self):
        """Create the local shortcuts for the CodeEditor."""
        shortcut_context_name_callbacks = (
            ('editor', 'code completion', self.do_completion),
            ('editor', 'duplicate line', self.duplicate_line),
            ('editor', 'copy line', self.copy_line),
            ('editor', 'delete line', self.delete_line),
            ('editor', 'move line up', self.move_line_up),
            ('editor', 'move line down', self.move_line_down),
            ('editor', 'go to new line', self.go_to_new_line),
            ('editor', 'go to definition', self.do_go_to_definition),
            ('editor', 'toggle comment', self.toggle_comment),
            ('editor', 'blockcomment', self.blockcomment),
            ('editor', 'unblockcomment', self.unblockcomment),
            ('editor', 'transform to uppercase', self.transform_to_uppercase),
            ('editor', 'transform to lowercase', self.transform_to_lowercase),
            ('editor', 'indent', lambda: self.indent(force=True)),
            ('editor', 'unindent', lambda: self.unindent(force=True)),
            ('editor', 'start of line',
             self.create_cursor_callback('StartOfLine')),
            ('editor', 'end of line',
             self.create_cursor_callback('EndOfLine')),
            ('editor', 'previous line', self.create_cursor_callback('Up')),
            ('editor', 'next line', self.create_cursor_callback('Down')),
            ('editor', 'previous char', self.create_cursor_callback('Left')),
            ('editor', 'next char', self.create_cursor_callback('Right')),
            ('editor', 'previous word',
             self.create_cursor_callback('PreviousWord')),
            ('editor', 'next word', self.create_cursor_callback('NextWord')),
            ('editor', 'kill to line end', self.kill_line_end),
            ('editor', 'kill to line start', self.kill_line_start),
            ('editor', 'yank', self._kill_ring.yank),
            ('editor', 'rotate kill ring', self._kill_ring.rotate),
            ('editor', 'kill previous word', self.kill_prev_word),
            ('editor', 'kill next word', self.kill_next_word),
            ('editor', 'start of document',
             self.create_cursor_callback('Start')),
            ('editor', 'end of document',
             self.create_cursor_callback('End')),
            ('editor', 'undo', self.undo),
            ('editor', 'redo', self.redo),
            ('editor', 'cut', self.cut),
            ('editor', 'copy', self.copy),
            ('editor', 'paste', self.paste),
            ('editor', 'delete', self.delete),
            ('editor', 'select all', self.selectAll),
            ('editor', 'docstring',
             self.writer_docstring.write_docstring_for_shortcut),
            ('array_builder', 'enter array inline', self.enter_array_inline),
            ('array_builder', 'enter array table', self.enter_array_table)
            )

        shortcuts = []
        for context, name, callback in shortcut_context_name_callbacks:
            shortcuts.append(
                config_shortcut(
                    callback, context=context, name=name, parent=self))
        return shortcuts