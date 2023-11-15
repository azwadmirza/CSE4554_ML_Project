    def analyze_graph(self, **kwargs):
        operand_infos = self._operand_infos
        chunk_graph = self.get_chunk_graph()

        # remove fetch chunk if exists
        if any(isinstance(c.op, Fetch) for c in chunk_graph):
            chunk_graph = chunk_graph.copy()
            for c in list(chunk_graph):
                if isinstance(c.op, Fetch):
                    chunk_graph.remove_node(c)

        if len(chunk_graph) == 0:
            return

        for n in chunk_graph:
            k = n.op.key
            succ_size = chunk_graph.count_successors(n)
            if k not in operand_infos:
                operand_infos[k] = dict(optimize=dict(
                    depth=0, demand_depths=(), successor_size=succ_size, descendant_size=0
                ))
            else:
                operand_infos[k]['optimize']['successor_size'] = succ_size

        worker_slots = self._get_worker_slots()
        self._assigned_workers = set(worker_slots)
        analyzer = GraphAnalyzer(chunk_graph, worker_slots)

        for k, v in analyzer.calc_depths().items():
            operand_infos[k]['optimize']['depth'] = v

        for k, v in analyzer.calc_descendant_sizes().items():
            operand_infos[k]['optimize']['descendant_size'] = v

        if kwargs.get('do_placement', True):
            logger.debug('Placing initial chunks for graph %s', self._graph_key)
            self._assign_initial_workers(analyzer)