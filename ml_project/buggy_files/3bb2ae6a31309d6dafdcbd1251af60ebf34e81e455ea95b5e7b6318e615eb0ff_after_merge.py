    def __move_cursor_position(self, index_move):
        """
        Move the cursor position forward or backward in the cursor
        position history by the specified index increment.
        """
        if self.cursor_pos_index is None:
            return
        filename, _position = self.cursor_pos_history[self.cursor_pos_index]
        self.cursor_pos_history[self.cursor_pos_index] = (
            filename, self.get_current_editor().get_position('cursor'))
        self.__ignore_cursor_position = True
        old_index = self.cursor_pos_index
        self.cursor_pos_index = min(len(self.cursor_pos_history) - 1,
                                    max(0, self.cursor_pos_index + index_move))
        filename, position = self.cursor_pos_history[self.cursor_pos_index]
        filenames = self.get_current_editorstack().get_filenames()
        if not osp.isfile(filename) and filename not in filenames:
            self.cursor_pos_history.pop(self.cursor_pos_index)
            if self.cursor_pos_index <= old_index:
                old_index -= 1
            self.cursor_pos_index = old_index
        else:
            self.load(filename)
            editor = self.get_current_editor()
            if position < editor.document().characterCount():
                editor.set_cursor_position(position)
        self.__ignore_cursor_position = False
        self.update_cursorpos_actions()