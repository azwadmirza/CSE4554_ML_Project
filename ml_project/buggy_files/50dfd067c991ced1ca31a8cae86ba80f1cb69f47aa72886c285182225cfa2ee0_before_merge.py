    def _update_ast(self):
        self.reset(partial_reset=True)
        self.is_snippet_active = True
        self.ast.compute_position(self.starting_position)
        start_line, start_column = self.starting_position
        visitor = SnippetSearcherVisitor(
            start_line, start_column, self.node_number)
        self.ast.accept(visitor)
        self.snippets_map = visitor.snippet_map
        self.update_position_tree(visitor)
        self.editor.clear_extra_selections('code_snippets')
        self.draw_snippets()