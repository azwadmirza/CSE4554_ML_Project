    def handle_save_files(self):
        """Save the open files."""
        editorstack = self.get_editorstack()
        if editorstack is not None:
            editorstack.save()