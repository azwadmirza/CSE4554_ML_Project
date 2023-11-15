    def on_file_updated(self, ed, elem, text):
        """Write the editor text into the form field and clean up tempfile.

        Callback for GUIProcess when the edited text was updated.

        Args:
            elem: The WebElementWrapper which was modified.
            text: The new text to insert.
        """
        try:
            elem.set_value(text)
        except webelem.OrphanedError as e:
            message.error('Edited element vanished')
            ed.backup()
        except webelem.Error as e:
            message.error(str(e))
            ed.backup()