    def _insert_snippet_at_node(self, leaf, snippet, new_node,
                                line, column):
        self.redo_stack = []
        value = leaf.value
        leaf_position = leaf.position
        if len(leaf_position) == 1:
            x, y = leaf_position[0]
            leaf_position = [(x, y), (x, y + 1)]

        leaf_start, leaf_end = leaf_position
        leaf_index = leaf.index_in_parent
        placeholder = snippet.placeholder
        text_tokens = list(placeholder.tokens)
        first_tokens = text_tokens[:leaf_index]
        second_tokens = text_tokens[leaf_index + 1:]
        if leaf_start == (line, column):
            single_token = False
            if len(text_tokens) == 1:
                possible_snippet = new_node.tokens[0]
                single_token = True
                if isinstance(possible_snippet, nodes.SnippetASTNode):
                    # Placeholder replacement
                    first_tokens = (
                        list(possible_snippet.placeholder.tokens) +
                        list(new_node.tokens[1:])
                    )
                    second_tokens = []
                else:
                    first_tokens = list(new_node.tokens)
                    second_tokens = []
            if not single_token:
                if isinstance(new_node, nodes.TextNode):
                    first_tokens += list(new_node.tokens)
                else:
                    first_tokens.append(new_node)
                if not new_node.text().startswith(value):
                    first_tokens.append(leaf)
        elif leaf_end == (line, column):
            first_tokens.append(leaf)
            first_tokens.append(new_node)
        else:
            _, start_pos = leaf_start
            diff = column - start_pos

            first_part = value[:diff]
            second_part = value[diff:]
            first_node = nodes.LeafNode(leaf.name, first_part)
            second_node = nodes.LeafNode(leaf.name, second_part)
            first_tokens.append(first_node)
            first_tokens.append(new_node)
            first_tokens.append(second_node)
        text_tokens = first_tokens + second_tokens
        placeholder.tokens = text_tokens