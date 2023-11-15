    def _open_editor_cb(self, elem):
        """Open editor after the focus elem was found in open_editor."""
        if elem is None:
            message.error("No element focused!")
            return
        if not elem.is_editable(strict=True):
            message.error("Focused element is not editable!")
            return

        text = elem.value()
        if text is None:
            message.error("Could not get text from the focused element.")
            return
        assert isinstance(text, str), text

        caret_position = elem.caret_position()

        ed = editor.ExternalEditor(watch=True, parent=self._tabbed_browser)
        ed.file_updated.connect(functools.partial(
            self.on_file_updated, elem))
        ed.editing_finished.connect(lambda: mainwindow.raise_window(
            objreg.last_focused_window(), alert=False))
        ed.edit(text, caret_position)