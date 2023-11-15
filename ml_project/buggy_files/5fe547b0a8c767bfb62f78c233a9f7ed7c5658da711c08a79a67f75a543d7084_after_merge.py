    def get_node_group(node) -> str:
        if 'group' in node and node['group']:
            return node['group']
        node_type = "exploited" if node.get("exploited") else "clean"
        node_os = NodeService.get_node_os(node)
        return NodeStates.get_by_keywords([node_type, node_os]).value