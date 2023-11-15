    def cursor_changed(self, line, col):
        if not rtree_available:
            return
        # with QMutexLocker(self.reset_lock):
        ignore_calls = {'undo', 'redo'}
        node, nearest_snippet, _ = self._find_node_by_position(line, col)
        if node is None:
            stack = inspect.stack()
            ignore = False
            # Check if parent call was due to text update on codeeditor
            # caused by a undo/redo call
            for call in stack:
                if call[3] in ignore_calls:
                    ignore = True
                    break
            if not ignore:
                self.reset()
        else:
            if nearest_snippet is not None:
                self.active_snippet = nearest_snippet.number