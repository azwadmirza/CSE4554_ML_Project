    def refresh_save_all_action(self):
        """Enable 'Save All' if there are files to be saved"""
        editorstack = self.get_current_editorstack()
        state = any(finfo.editor.document().isModified()
                    for finfo in editorstack.data)
        self.save_all_action.setEnabled(state)