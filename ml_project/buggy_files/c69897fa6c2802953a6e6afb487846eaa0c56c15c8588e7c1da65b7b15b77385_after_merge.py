    def update_check_graph(self, deps_graph, output):
        """ update the lockfile, checking for security that only nodes that are being built
        from sources can change their PREF, or nodes that depend on some other "modified"
        package, because their binary-id can change too
        """

        affected = self._closure_affected()
        for node in deps_graph.nodes:
            if node.recipe == RECIPE_VIRTUAL:
                continue
            try:
                lock_node = self._nodes[node.id]
            except KeyError:
                if node.recipe == RECIPE_CONSUMER:
                    continue  # If the consumer node is not found, could be a test_package
                raise
            if lock_node.pref:
                pref = lock_node.pref if self.revisions_enabled else lock_node.pref.copy_clear_revs()
                node_pref = node.pref if self.revisions_enabled else node.pref.copy_clear_revs()
                # If the update is compatible (resolved complete PREV) or if the node has
                # been build, then update the graph
                if (pref.id == PACKAGE_ID_UNKNOWN or pref.is_compatible_with(node_pref) or
                        node.binary == BINARY_BUILD or node.id in affected or
                        node.recipe == RECIPE_CONSUMER):
                    lock_node.pref = node.pref
                else:
                    raise ConanException("Mismatch between lock and graph:\nLock:  %s\nGraph: %s"
                                         % (repr(pref), repr(node.pref)))