    def _collect_operand_io_meta(graph, chunks):
        # collect operand i/o information
        predecessor_keys = set()
        successor_keys = set()
        input_chunk_keys = set()
        shared_input_chunk_keys = set()
        pure_dep_chunk_keys = set()
        no_prepare_chunk_keys = set()
        chunk_keys = set()
        shuffle_keys = dict()
        predecessors_to_successors = dict()

        for c in chunks:
            # handling predecessor args
            for pn in graph.iter_predecessors(c):
                if not isinstance(pn.op, Fetch):
                    predecessor_keys.add(pn.op.key)
                input_chunk_keys.add(pn.key)
                if graph.count_successors(pn) > 1:
                    shared_input_chunk_keys.add(pn.key)

            for inp, prep in zip(c.op.inputs or (), c.op.prepare_inputs):
                if not prep and inp.key in input_chunk_keys:
                    no_prepare_chunk_keys.add(inp.key)

            for inp, is_dep in zip(c.op.inputs or (), c.op.pure_depends):
                if is_dep and inp.key in input_chunk_keys:
                    pure_dep_chunk_keys.add(inp.key)

            # handling successor args
            for sn in graph.iter_successors(c):
                successor_keys.add(sn.op.key)
            if isinstance(c.op, ShuffleProxy):
                for sn in graph.iter_successors(c):
                    shuffle_keys[sn.op.key] = get_chunk_shuffle_key(sn)
            if isinstance(c.op, SuccessorsExclusive):
                for sn in graph.iter_successors(c):
                    predecessors_to_successors[sn.inputs[0].op.key] = sn.op.key

            chunk_keys.update(co.key for co in c.op.outputs)

        io_meta = dict(
            predecessors=list(predecessor_keys),
            successors=list(successor_keys),
            input_chunks=list(input_chunk_keys),
            no_prepare_chunk_keys=list(no_prepare_chunk_keys),
            pure_dep_chunk_keys=list(pure_dep_chunk_keys),
            shared_input_chunks=list(shared_input_chunk_keys),
            chunks=list(chunk_keys),
        )
        if shuffle_keys:
            io_meta['shuffle_keys'] = [shuffle_keys.get(k) for k in io_meta['successors']]
        if predecessors_to_successors:
            io_meta['predecessors_to_successors'] = predecessors_to_successors
        return io_meta