    def update_editor(self, items, editor=None):
        """
        Update the outline explorer for `editor` preserving the tree
        state.
        """
        plugin_base = self.parent().parent()
        if editor is None:
            editor = self.current_editor
        editor_id = editor.get_id()
        language = editor.get_language()
        update = self.update_tree(items, editor_id, language)

        if getattr(plugin_base, "_isvisible", True) and update:
            self.save_expanded_state()
            self.restore_expanded_state()
            self.do_follow_cursor()