    def renamed(self, source, dest):
        """
        Propagate file rename to editor stacks and autosave component.

        This function is called when a file is renamed in the file explorer
        widget or the project explorer.
        """
        filename = osp.abspath(to_text_string(source))
        index = self.editorstacks[0].has_filename(filename)
        if index is not None:
            for editorstack in self.editorstacks:
                editorstack.rename_in_data(filename,
                                           new_filename=to_text_string(dest))
        self.editorstacks[0].autosave.file_renamed(
            filename, to_text_string(dest))