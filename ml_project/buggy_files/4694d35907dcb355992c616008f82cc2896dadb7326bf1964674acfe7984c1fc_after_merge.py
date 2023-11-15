    def _find_node_by_position(self, line, col):
        point = (line, col) * 2
        node_numbers = list(self.index.intersection(point))
        current_node, nearest_text, nearest_snippet = None, None, None

        if len(node_numbers) > 0:
            for node_number in node_numbers:
                current_node = self.node_position[node_number][-1]
                if isinstance(current_node, nodes.SnippetASTNode):
                    nearest_snippet = current_node
                elif isinstance(current_node, nodes.TextNode):
                    if node_number != 0:
                        nearest_text = current_node
                elif isinstance(current_node, nodes.LeafNode):
                    if current_node.name == 'EPSILON':
                        break

        if nearest_text is not None:
            node_id = id(current_node)
            text_ids = set([id(token) for token in nearest_text.tokens])
            if node_id not in text_ids:
                current_node = nearest_text.tokens[-1]
        return current_node, nearest_snippet, nearest_text