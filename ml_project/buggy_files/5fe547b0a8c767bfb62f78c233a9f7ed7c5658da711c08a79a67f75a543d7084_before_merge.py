    def get_node_group(node):
        node_type = "exploited" if node.get("exploited") else "clean"
        node_os = NodeService.get_node_os(node)
        return "%s_%s" % (node_type, node_os)