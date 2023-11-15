    def _collect_operand_io_meta(graph, chunks):
        # collect operand i/o information
        predecessor_keys = set()
        successor_keys = set()
        input_chunk_keys = set()
        shared_input_chunk_keys = set()
        chunk_keys = set()

        for c in chunks:
            # handling predecessor args
            for pn in graph.iter_predecessors(c):
                predecessor_keys.add(pn.op.key)
                input_chunk_keys.add(pn.key)
                if graph.count_successors(pn) > 1:
                    shared_input_chunk_keys.add(pn.key)

            # handling successor args
            for sn in graph.iter_successors(c):
                successor_keys.add(sn.op.key)

            chunk_keys.update(co.key for co in c.op.outputs)

        io_meta = dict(
            predecessors=set(predecessor_keys),
            successors=set(successor_keys),
            input_chunks=set(input_chunk_keys),
            shared_input_chunks=set(shared_input_chunk_keys),
            chunks=set(chunk_keys),
        )
        return io_meta