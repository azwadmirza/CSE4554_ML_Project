    def evaluate_graph(self, deps_graph, build_mode, update, remote_name):
        evaluated_references = {}
        for node in deps_graph.nodes:
            if not node.conan_ref:
                continue

            private_neighbours = node.private_neighbors()
            if private_neighbours:
                self._evaluate_node(node, build_mode, update, evaluated_references, remote_name)
                if node.binary != BINARY_BUILD:
                    for neigh in private_neighbours:
                        neigh.binary = BINARY_SKIP
                        closure = deps_graph.full_closure(neigh)
                        for n in closure:
                            n.binary = BINARY_SKIP

        for node in deps_graph.nodes:
            if not node.conan_ref or node.binary:
                continue
            self._evaluate_node(node, build_mode, update, evaluated_references, remote_name)