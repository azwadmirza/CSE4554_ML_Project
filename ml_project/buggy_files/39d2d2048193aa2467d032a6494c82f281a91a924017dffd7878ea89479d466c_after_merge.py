    def insert_text(self, text, line, column):
        has_selected_text = self.editor.has_selected_text()
        start, end = self.editor.get_selection_start_end()
        if has_selected_text:
            self._remove_selection(start, end)
            line, column = start
        node, snippet, text_node = self._find_node_by_position(line, column)
        if node is None:
            self.reset()
            return
        tokens = tokenize(text)
        token_nodes = [nodes.LeafNode(t.token, t.value) for t in tokens]
        for token in token_nodes:
            token.compute_position((line, column))
        if node.name == 'EPSILON':
            new_text_node = nodes.TextNode(*token_nodes)
            snippet.placeholder = new_text_node
            return
        position = node.position
        if len(position) == 1:
            x, y = position[0]
            position = ((x, y), (x, y + 1))
        leaf_start, leaf_end = position
        node_index = node.index_in_parent
        text_node_tokens = list(text_node.tokens)

        if (line, column) == leaf_start:
            left_offset = 0
            right_offset = 0
            first_token = token_nodes[0]
            last_token = token_nodes[-1]
            if node_index > 0 and len(text_node_tokens) > 1:
                previous_node = text_node_tokens[node_index - 1]
                if first_token.mark_for_position:
                    if first_token.name in MERGE_ALLOWED:
                        if first_token.name == previous_node.name:
                            left_offset = 1
                            first_token.value = (
                                previous_node.value + first_token.value)
            if last_token.mark_for_position:
                if last_token.name in MERGE_ALLOWED:
                    if last_token.name == node.name:
                        right_offset = 1
                        last_token.value = (
                            last_token.value + node.value)
            text_node_tokens = (
                text_node_tokens[:node_index - left_offset] +
                token_nodes +
                text_node_tokens[node_index + right_offset:]
            )
        elif (line, column) == leaf_end:
            left_offset = -1
            right_offset = 1
            first_token = token_nodes[0]
            last_token = token_nodes[-1]
            if node_index >= 1 and node_index < len(text_node_tokens) - 1:
                next_node = text_node_tokens[node_index + 1]
                if last_token.mark_for_position:
                    if last_token.name in MERGE_ALLOWED:
                        if last_token.name == next_node.name:
                            right_offset = 2
                            last_token.value = (
                                last_token.value + next_node.value)

            if first_token.mark_for_position:
                if first_token.name in MERGE_ALLOWED:
                    if first_token.name == node.name:
                        left_offset = 0
                        first_token.value = (
                            node.value + first_token.value)

            text_node_tokens = (
                text_node_tokens[:node_index - left_offset] +
                token_nodes +
                text_node_tokens[node_index + right_offset:]
            )
        else:
            _, start_pos = leaf_start
            diff = column - start_pos
            value = node.value
            first_tokens = text_node_tokens[:node_index]
            second_tokens = text_node_tokens[node_index + 1:]
            first_part = value[:diff]
            second_part = value[diff:]
            first_token = token_nodes[0]
            last_token = token_nodes[-1]
            left_merge = False
            if first_token.mark_for_position:
                if first_token.name in MERGE_ALLOWED:
                    if first_token == node.name:
                        left_merge = True
                        first_token.value = first_part + first_token.value
            if not left_merge:
                first_tokens.append(nodes.LeafNode(node.name, first_part))

            right_merge = False
            if last_token.mark_for_position:
                if last_token.name in MERGE_ALLOWED:
                    if last_token == node.name:
                        right_merge = True
                        last_token.value = last_token.value + second_part
            if not right_merge:
                second_tokens.insert(0, nodes.LeafNode(node.name, second_part))

            text_node_tokens = first_tokens + token_nodes + second_tokens

        text_node.tokens = text_node_tokens