    def cursor_changed(self, line, col):
        if not rtree_available:
            return
        node, nearest_snippet, _ = self._find_node_by_position(line, col)
        if node is None:
            # self.reset()
            pass
        else:
            if nearest_snippet is not None:
                self.active_snippet = nearest_snippet.number