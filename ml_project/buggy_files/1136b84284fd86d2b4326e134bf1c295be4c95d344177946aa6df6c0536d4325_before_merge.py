    def editorstack_closed(self):
        logger.debug("method 'editorstack_closed':")
        logger.debug("    self  : %r" % self)
        try:
            self.unregister_editorstack_cb(self.editorstack)
            self.editorstack = None
            close_splitter = self.count() == 1
        except RuntimeError:
            # editorsplitter has been destroyed (happens when closing a
            # EditorMainWindow instance)
            return
        if close_splitter:
            # editorstack just closed was the last widget in this QSplitter
            self.close()
            return
        self.__give_focus_to_remaining_editor()