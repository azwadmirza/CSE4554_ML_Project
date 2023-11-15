    def key(node: FineGrainedDeferredNode) -> int:
        # Unlike modules which are sorted by name within SCC,
        # nodes within the same module are sorted by line number, because
        # this is how they are processed in normal mode.
        return node.node.line