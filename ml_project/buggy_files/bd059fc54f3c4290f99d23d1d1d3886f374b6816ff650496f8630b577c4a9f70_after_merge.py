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

        ed = editor.ExternalEditor(self._tabbed_browser)
        ed.editing_finished.connect(functools.partial(
            self.on_editing_finished, elem))
        tab = self._current_widget()
        tab.shutting_down.connect(functools.partial(
            self.on_editor_orphaned, ed))
        ed.edit(text, caret_position)