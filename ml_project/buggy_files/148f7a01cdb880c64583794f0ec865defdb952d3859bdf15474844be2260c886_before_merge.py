    def _undo(self):
        if self.is_snippet_active:
            if len(self.undo_stack) > 0:
                info = self.undo_stack.pop(0)
                ast_copy = copy.deepcopy(self.ast)
                redo_info = (ast_copy, self.starting_position,
                             self.active_snippet)
                self.redo_stack.insert(0, redo_info)
                self.ast, self.starting_position, self.active_snippet = info
                self._update_ast()
                self.editor.clear_extra_selections('code_snippets')
                self.draw_snippets()