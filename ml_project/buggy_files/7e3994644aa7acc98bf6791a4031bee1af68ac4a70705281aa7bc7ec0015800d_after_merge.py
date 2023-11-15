    def assign_operand_workers(self, op_keys, input_chunk_metas=None, analyzer=None):
        operand_infos = self._operand_infos
        chunk_graph = self.get_chunk_graph()

        if analyzer is None:
            analyzer = GraphAnalyzer(chunk_graph, self._get_worker_slots())
        assignments = analyzer.calc_operand_assignments(op_keys, input_chunk_metas=input_chunk_metas)
        for idx, (k, v) in enumerate(assignments.items()):
            operand_infos[k]['optimize']['placement_order'] = idx
            operand_infos[k]['target_worker'] = v
        return assignments