    def prepare_graph(self, compose=True):
        """
        Tile and compose tensor graph into chunk graph
        :param compose: if True, do compose after tiling
        """
        tensor_graph = deserialize_graph(self._serialized_tensor_graph)
        self._tensor_graph_cache = tensor_graph

        logger.debug('Begin preparing graph %s with %d tensors to chunk graph.',
                     self._graph_key, len(tensor_graph))

        # mark target tensor steps
        if not self._target_tensor_chunk_ops:
            for tn in tensor_graph:
                if not tensor_graph.count_successors(tn):
                    self._target_tensor_chunk_ops[tn.key] = set()
                    self._target_tensor_finished[tn.key] = set()

        if self._serialized_chunk_graph:
            serialized_chunk_graph = self._serialized_chunk_graph
            chunk_graph = DAG.from_pb(serialized_chunk_graph)
        else:
            chunk_graph = DAG()

        key_to_chunk = {c.key: c for c in chunk_graph}

        tensor_key_opid_to_tiled = self._tensor_key_opid_to_tiled

        for t in tensor_graph:
            self._tensor_key_to_opid[t.key] = t.op.id
            if (t.key, t.op.id) not in tensor_key_opid_to_tiled:
                continue
            t._chunks = [key_to_chunk[k] for k in [tensor_key_opid_to_tiled[(t.key, t.op.id)][-1]]]

        tq = deque()
        for t in tensor_graph:
            if t.inputs and not all((ti.key, ti.op.id) in tensor_key_opid_to_tiled for ti in t.inputs):
                continue
            tq.append(t)

        while tq:
            tensor = tq.popleft()
            if not tensor.is_coarse() or (tensor.key, tensor.op.id) in tensor_key_opid_to_tiled:
                continue
            inputs = [tensor_key_opid_to_tiled[(it.key, it.op.id)][-1] for it in tensor.inputs or ()]

            op = tensor.op.copy()
            _ = op.new_tensors(inputs, [o.shape for o in tensor.op.outputs],  # noqa: F841
                               dtype=[o.dtype for o in tensor.op.outputs], **tensor.params)

            total_tiled = []
            for j, t, to_tile in zip(itertools.count(0), tensor.op.outputs, op.outputs):
                # replace inputs with tiled ones
                if not total_tiled:
                    try:
                        td = handler.dispatch(to_tile)
                    except DataNotReady:
                        continue

                    if isinstance(td, (tuple, list)):
                        total_tiled.extend(td)
                    else:
                        total_tiled.append(td)

                tiled = total_tiled[j]
                tensor_key_opid_to_tiled[(t.key, t.op.id)].append(tiled)

                # add chunks to fine grained graph
                q = deque([tiled_c.data for tiled_c in tiled.chunks])
                input_chunk_keys = set(itertools.chain(*([(it.key, it.id) for it in input.chunks]
                                                         for input in to_tile.inputs)))
                while len(q) > 0:
                    c = q.popleft()
                    if (c.key, c.id) in input_chunk_keys:
                        continue
                    if c not in chunk_graph:
                        chunk_graph.add_node(c)
                    for ic in c.inputs or []:
                        if ic not in chunk_graph:
                            chunk_graph.add_node(ic)
                            q.append(ic)
                        chunk_graph.add_edge(ic, c)

                for succ in tensor_graph.successors(t):
                    if any((t.key, t.op.id) not in tensor_key_opid_to_tiled for t in succ.inputs):
                        continue
                    tq.append(succ)

        # record the chunk nodes in graph
        reserve_chunk = set()
        result_chunk_keys = list()
        for tk_topid in tensor_key_opid_to_tiled:
            for n in [c.data for t in tensor_key_opid_to_tiled[tk_topid] for c in t.chunks]:
                result_chunk_keys.append(n.key)
                dq_predecessors = deque([n])
                while dq_predecessors:
                    current = dq_predecessors.popleft()
                    reserve_chunk.update(n.op.outputs)
                    predecessors = chunk_graph.predecessors(current)
                    dq_predecessors.extend([p for p in predecessors if p not in reserve_chunk])
                    reserve_chunk.update(predecessors)
        # delete redundant chunk
        for n in list(chunk_graph.iter_nodes()):
            if n not in reserve_chunk:
                chunk_graph.remove_node(n)

        if compose:
            chunk_graph.compose(keys=result_chunk_keys)

        for tk, topid in tensor_key_opid_to_tiled:
            if tk not in self._target_tensor_chunk_ops:
                continue
            for n in tensor_key_opid_to_tiled[(tk, topid)][-1].chunks:
                self._terminal_chunk_op_tensor[n.op.key].add(tk)
                self._target_tensor_chunk_ops[tk].add(n.op.key)

        # sync chunk graph to kv store
        if self._kv_store_ref is not None:
            graph_path = '/sessions/%s/graphs/%s' % (self._session_id, self._graph_key)
            self._kv_store_ref.write('%s/chunk_graph' % graph_path,
                                     serialize_graph(chunk_graph, compress=True), _tell=True, _wait=False)

        self._nodes_num = len(chunk_graph)
        self._chunk_graph_cache = chunk_graph
        for n in self._chunk_graph_cache:
            self._op_key_to_chunk[n.op.key].append(n)