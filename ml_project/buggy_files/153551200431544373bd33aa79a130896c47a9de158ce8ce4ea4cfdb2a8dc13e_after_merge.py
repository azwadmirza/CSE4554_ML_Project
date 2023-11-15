    def apply(self, **kwargs):
        # type: (Any) -> None
        for node in self.document.traverse(addnodes.index):
            for i, entries in enumerate(node['entries']):
                if len(entries) == 4:
                    source, line = get_source_line(node)
                    warnings.warn('An old styled index node found: %r at (%s:%s)' %
                                  (node, source, line), RemovedInSphinx40Warning)
                    node['entries'][i] = entries + (None,)