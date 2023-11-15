    def set_id(self, node: Element, msgnode: Element = None,
               suggested_prefix: str = '') -> str:
        from sphinx.util import docutils
        if docutils.__version_info__ >= (0, 16):
            ret = super().set_id(node, msgnode, suggested_prefix)  # type: ignore
        else:
            ret = super().set_id(node, msgnode)

        if docutils.__version_info__ < (0, 17):
            # register other node IDs forcedly
            for node_id in node['ids']:
                if node_id not in self.ids:
                    self.ids[node_id] = node

        return ret