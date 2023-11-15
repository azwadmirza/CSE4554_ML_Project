    def execute_graph(self, graph, keys, n_parallel=None, print_progress=False,
                      mock=False, no_intermediate=False, compose=True, retval=True,
                      chunk_result=None):
        """
        :param graph: graph to execute
        :param keys: result keys
        :param n_parallel: num of max parallelism
        :param print_progress:
        :param compose: if True. fuse nodes when possible
        :param mock: if True, only estimate data sizes without execution
        :param no_intermediate: exclude intermediate data sizes when estimating memory size
        :param retval: if True, keys specified in argument keys is returned
        :param chunk_result: dict to put chunk key to chunk data, if None, use self.chunk_result
        :return: execution result
        """
        optimized_graph = self._preprocess(graph, keys) if compose else graph

        if not mock:
            # fetch_keys only useful when calculating sizes
            fetch_keys = set()
        else:
            fetch_keys = set(v.key for v in graph if isinstance(v.op, Fetch))
            for c in graph:
                if graph.count_predecessors(c) != 0:
                    continue
                fetch_keys.update(inp.key for inp in c.inputs or ())

        executed_keys = list(itertools.chain(*[v[1] for v in self.stored_tileables.values()]))
        chunk_result = self._chunk_result if chunk_result is None else chunk_result
        graph_execution = GraphExecution(chunk_result, optimized_graph,
                                         keys, executed_keys, self._sync_provider,
                                         n_parallel=n_parallel, engine=self._engine,
                                         prefetch=self._prefetch, print_progress=print_progress,
                                         mock=mock, mock_max_memory=self._mock_max_memory,
                                         fetch_keys=fetch_keys, no_intermediate=no_intermediate)
        res = graph_execution.execute(retval)
        self._mock_max_memory = max(self._mock_max_memory, graph_execution._mock_max_memory)
        if mock:
            self._chunk_result.clear()
        return res