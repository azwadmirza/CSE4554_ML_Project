    def _get_keys_to_fetch(graph):
        from ..operands import Fetch, FetchShuffle
        fetch_keys = set()
        exclude_fetch_keys = set()
        for chunk in graph:
            if isinstance(chunk.op, Fetch):
                fetch_keys.add(chunk.op.to_fetch_key or chunk.key)
            elif isinstance(chunk.op, FetchShuffle):
                shuffle_key = get_chunk_shuffle_key(graph.successors(chunk)[0])
                for k in chunk.op.to_fetch_keys:
                    fetch_keys.add((k, shuffle_key))
            else:
                for inp, prepare_inp in zip(chunk.inputs, chunk.op.prepare_inputs):
                    if not prepare_inp:
                        exclude_fetch_keys.add(inp.key)
        return list(fetch_keys - exclude_fetch_keys)