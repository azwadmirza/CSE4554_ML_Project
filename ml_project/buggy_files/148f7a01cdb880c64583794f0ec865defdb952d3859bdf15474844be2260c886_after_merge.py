    def _undo(self):
        if len(self.undo_stack) == 0:
            self.reset()
        if self.is_snippet_active:
            num_pops = 0
            patch = self.editor.patch
            for diffs in patch:
                for (op, data) in diffs.diffs:
                    if op in VALID_UPDATES:
                        num_pops += len(data)
            if len(self.undo_stack) > 0:
                for _ in range(num_pops):
                    if len(self.undo_stack) == 0:
                        break
                    info = self.undo_stack.pop(0)
                    ast_copy = copy.deepcopy(self.ast)
                    redo_info = (ast_copy, self.starting_position,
                                 self.active_snippet)
                    self.redo_stack.insert(0, redo_info)
                    self.ast, self.starting_position, self.active_snippet = info
                self._update_ast()
                self.editor.clear_extra_selections('code_snippets')
                self.draw_snippets()