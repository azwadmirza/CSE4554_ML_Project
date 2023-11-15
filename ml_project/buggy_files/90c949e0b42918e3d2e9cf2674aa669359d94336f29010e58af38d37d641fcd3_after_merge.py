    def current_changed(self, index):
        """Stack index has changed"""
#        count = self.get_stack_count()
#        for btn in (self.filelist_btn, self.previous_btn, self.next_btn):
#            btn.setEnabled(count > 1)

        editor = self.get_current_editor()
        if editor.lsp_ready and not editor.document_opened:
            editor.document_did_open()
        if index != -1:
            editor.setFocus()
            logger.debug("Set focus to: %s" % editor.filename)
        else:
            self.reset_statusbar.emit()
        self.opened_files_list_changed.emit()

        self.stack_history.refresh()
        self.stack_history.remove_and_append(index)

        # Needed to avoid an error generated after moving/renaming
        # files outside Spyder while in debug mode.
        # See issue 8749.
        try:
            logger.debug("Current changed: %d - %s" %
                         (index, self.data[index].editor.filename))
        except IndexError:
            pass

        self.update_plugin_title.emit()
        if editor is not None:
            # Needed in order to handle the close of files open in a directory
            # that has been renamed. See issue 5157
            try:
                self.current_file_changed.emit(self.data[index].filename,
                                               editor.get_position('cursor'))
            except IndexError:
                pass