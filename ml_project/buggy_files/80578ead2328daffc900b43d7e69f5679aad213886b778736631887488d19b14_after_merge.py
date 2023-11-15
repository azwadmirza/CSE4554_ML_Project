    def dropEvent(self, event):
        """Reimplement Qt method
        Unpack dropped data and handle it"""
        source = event.mimeData()
        # The second check is necessary when mimedata2url(source)
        # returns None.
        # Fixes issue 7742
        if source.hasUrls() and mimedata2url(source):
            files = mimedata2url(source)
            files = [f for f in files if encoding.is_text_file(f)]
            files = set(files or [])
            for fname in files:
                self.plugin_load.emit(fname)
        elif source.hasText():
            editor = self.get_current_editor()
            if editor is not None:
                editor.insert_text(source.text())
        else:
            event.ignore()
        event.acceptProposedAction()