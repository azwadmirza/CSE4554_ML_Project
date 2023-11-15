    def __refresh_statusbar(self, index):
        """Refreshing statusbar widgets"""
        if self.data and len(self.data) > index:
            finfo = self.data[index]
            self.encoding_changed.emit(finfo.encoding)
            # Refresh cursor position status:
            line, index = finfo.editor.get_cursor_line_column()
            self.sig_editor_cursor_position_changed.emit(line, index)