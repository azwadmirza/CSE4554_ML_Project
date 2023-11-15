    def node_to_string(self, node):
        if node is None:
            return "<Unknown>"
        if not hasattr(node, 'name'):
            # we probably failed to parse a block, so we can't know the name
            return '{} ({})'.format(
                node.resource_type,
                node.original_file_path
            )
        return "{} {} ({})".format(
            node.resource_type,
            node.name,
            node.original_file_path)