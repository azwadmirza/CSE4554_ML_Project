    def _redo(self):
        if self.is_snippet_active:
            if len(self.redo_stack) > 0:
                info = self.redo_stack.pop(0)
                ast_copy = copy.deepcopy(self.ast)
                undo_info = (ast_copy, self.starting_position,
                             self.active_snippet)
                self.undo_stack.insert(0, undo_info)
                self.ast, self.starting_position, self.active_snippet = info
                self._update_ast()
                self.editor.clear_extra_selections('code_snippets')
                self.draw_snippets()