    def collect_1q_runs(self):
        """Return a set of non-conditional runs of 1q "op" nodes."""

        def filter_fn(node):
            return node.type == 'op' and len(node.qargs) == 1 \
                and len(node.cargs) == 0 and node.condition is None \
                and not node.op.is_parameterized() \
                and isinstance(node.op, Gate) \
                and hasattr(node.op, '__array__')

        group_list = rx.collect_runs(self._multi_graph, filter_fn)
        return set(tuple(x) for x in group_list)