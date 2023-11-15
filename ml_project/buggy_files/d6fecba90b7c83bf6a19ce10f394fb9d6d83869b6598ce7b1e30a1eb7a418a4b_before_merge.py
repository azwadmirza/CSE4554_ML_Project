    def _delete_token(self, node, text_node, line, column):
        node_position = node.position
        text_node_tokens = list(text_node.tokens)
        node_index = node.index_in_parent
        if len(node_position) == 1:
            # Single character removal
            if node_index > 0 and node_index + 1 < len(text_node_tokens):
                left_node = text_node_tokens[node_index - 1]
                right_node = text_node_tokens[node_index + 1]
                offset = 1
                if left_node.mark_for_position:
                    if left_node.name in MERGE_ALLOWED:
                        if left_node.name == right_node.name:
                            left_node.value = (
                                left_node.value + right_node.value)
                            offset = 2
                text_node_tokens = (
                    text_node_tokens[:node_index] +
                    text_node_tokens[node_index + offset:]
                )
            else:
                text_node_tokens.pop(node_index)
        else:
            node_start, node_end = node_position
            if node_start == (line, column):
                previous_token = text_node_tokens[node_index - 1]
                previous_value = previous_token.value
                previous_value = previous_value[:-1]
                merge = True
                diff = 0
                if len(previous_value) == 0:
                    if node_index - 2 > 0:
                        previous_token = text_node_tokens[node_index - 2]
                    else:
                        merge = False
                    text_node_tokens.pop(node_index - 1)
                    diff = 1
                else:
                    previous_token.value = previous_value

                if merge:
                    if node.mark_for_position:
                        if node.name in MERGE_ALLOWED:
                            if node.name == previous_token.name:
                                previous_token.value = (
                                    previous_token.value + node.value)
                                text_node_tokens.pop(node_index - diff)
            elif node_end == (line, column):
                node_value = node.value
                node_value = node_value[:-1]
                if len(node_value) == 0:
                    text_node_tokens.pop(node_index)
                else:
                    node.value = node_value
            else:
                x, y = node_start
                diff = column - y
                node_value = node.value
                node_value = node_value[:diff] + node_value[diff + 1:]
                node.value = node_value
        if len(text_node_tokens) == 0:
            text_node_tokens = [nodes.LeafNode()]
        text_node.tokens = text_node_tokens