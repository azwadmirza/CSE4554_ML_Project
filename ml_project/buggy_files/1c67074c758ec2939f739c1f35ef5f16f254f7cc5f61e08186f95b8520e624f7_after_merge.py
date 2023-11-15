    def delete_text(self, line, column):
        has_selected_text = self.editor.has_selected_text()
        start, end = self.editor.get_selection_start_end()
        if has_selected_text:
            self._remove_selection(start, end)
            return
        node, snippet, text_node = self._find_node_by_position(line, column)
        leaf_kind = node.name
        node_position = node.position
        if len(node_position) == 1:
            # Single, terminal node
            x, y = node_position[0]
            node_position = ((x, y), (x, y))

        first_text_position = text_node.position[0][0]
        first_text_start, first_text_end = first_text_position
        node_start, node_end = node_position
        if first_text_position == (line, column):
            # Snippet is dissolved and replaced by its own text
            snippet_number = snippet.number
            snippet_position = snippet.index_in_parent
            text_parent = snippet.parent
            parent_tokens = list(text_parent.tokens)
            parent_tokens = (parent_tokens[:snippet_position] +
                             list(snippet.placeholder.tokens) +
                             parent_tokens[snippet_position + 1:])
            text_parent.tokens = parent_tokens

            if len(parent_tokens) > 1:
                delete_token = parent_tokens[snippet_position - 1]
                # NOTE: There might be some problems if the previous token
                # is also a snippet
                self._delete_token(delete_token, text_parent, line, column)

            next_number = snippet_number
            for current_number in self.snippets_map:
                if current_number > snippet_number:
                    snippet_nodes = self.snippets_map[current_number]
                    for snippet_node in snippet_nodes:
                        current_number = snippet_node.number
                        snippet_node.number = next_number
                        next_number = current_number
                    # next_number -= 1
        else:
            self._delete_token(node, text_node, line, column)