    def calc_operand_assignments(self, op_keys, input_chunk_metas=None):
        """
        Decide target worker for given chunks.

        :param op_keys: keys of operands to assign
        :param input_chunk_metas: chunk metas for graph-level inputs, grouped by initial chunks
        :type input_chunk_metas: dict[str, dict[str, mars.scheduler.chunkmeta.WorkerMeta]]
        :return: dict mapping operand keys into worker endpoints
        """
        graph = self._graph
        op_states = self._op_states
        cur_assigns = self._fixed_assigns.copy()

        key_to_chunks = defaultdict(list)
        for n in graph:
            key_to_chunks[n.op.key].append(n)

        descendant_readies = set()
        op_keys = set(op_keys)
        chunks_to_assign = [key_to_chunks[k][0] for k in op_keys]

        if any(graph.count_predecessors(c) for c in chunks_to_assign):
            graph = graph.copy()
            for c in graph:
                if c.op.key not in op_keys:
                    continue
                for pred in graph.predecessors(c):
                    graph.remove_edge(pred, c)

        assigned_counts = defaultdict(lambda: 0)
        worker_op_keys = defaultdict(set)
        if cur_assigns:
            for op_key, state in op_states.items():
                if op_key not in op_keys and state == OperandState.READY \
                        and op_key in cur_assigns:
                    descendant_readies.add(op_key)
                    assigned_counts[cur_assigns[op_key]] += 1

        # calculate the number of nodes to be assigned to every worker
        # given number of workers and existing assignments
        pre_worker_quotas = self._calc_worker_assign_limits(
            len(chunks_to_assign) + len(descendant_readies), assigned_counts)

        # pre-assign nodes given pre-determined transfer sizes
        if not input_chunk_metas:
            worker_quotas = pre_worker_quotas
        else:
            for op_key, worker in self._iter_assignments_by_transfer_sizes(
                    pre_worker_quotas, input_chunk_metas):
                if op_key in cur_assigns:
                    continue
                assigned_counts[worker] += 1
                cur_assigns[op_key] = worker
                worker_op_keys[worker].add(op_key)

            worker_quotas = self._calc_worker_assign_limits(
                len(chunks_to_assign) + len(descendant_readies), assigned_counts)

        if cur_assigns:
            # calculate ranges of nodes already assigned
            for op_key, worker in self._iter_successor_assigns(cur_assigns):
                cur_assigns[op_key] = worker
                worker_op_keys[worker].add(op_key)

        logger.debug('Worker assign quotas: %r', worker_quotas)

        # calculate expected descendant count (spread range) of
        # every worker and subtract assigned number from it
        average_spread_range = len(graph) * 1.0 / len(self._worker_slots)
        spread_ranges = defaultdict(lambda: average_spread_range)
        for worker in cur_assigns.values():
            spread_ranges[worker] -= 1

        logger.debug('Scan spread ranges: %r', dict(spread_ranges))

        # assign pass 1: assign from fixed groups
        sorted_workers = sorted(worker_op_keys, reverse=True, key=lambda k: len(worker_op_keys[k]))
        for worker in sorted_workers:
            start_chunks = reduce(operator.add, (key_to_chunks[op_key] for op_key in worker_op_keys[worker]))
            self._assign_by_bfs(start_chunks, worker, worker_quotas, spread_ranges,
                                op_keys, cur_assigns, graph=graph)

        # assign pass 2: assign from other nodes to be assigned
        sorted_candidates = [v for v in chunks_to_assign]
        while max(worker_quotas.values()):
            worker = max(worker_quotas, key=lambda k: worker_quotas[k])
            cur = sorted_candidates.pop()
            while cur.op.key in cur_assigns:
                cur = sorted_candidates.pop()
            self._assign_by_bfs(cur, worker, worker_quotas, spread_ranges, op_keys,
                                cur_assigns, graph=graph)

        return dict((n.op.key, cur_assigns[n.op.key]) for n in chunks_to_assign)