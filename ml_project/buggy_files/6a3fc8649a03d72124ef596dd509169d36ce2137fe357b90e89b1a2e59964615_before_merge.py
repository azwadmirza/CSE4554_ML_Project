    def get_executable_operand_dag(self, op_key, serialize=True):
        """
        Make an operand into a worker-executable dag
        :param op_key: operand key
        :param serialize: whether to return serialized dag
        """
        graph = DAG()

        inputs_to_copied = dict()
        for c in self._op_key_to_chunk[op_key]:
            for inp in set(c.inputs or ()):
                op = TensorFetch(dtype=inp.dtype)
                inp_chunk = op.new_chunk(None, inp.shape, _key=inp.key).data
                inputs_to_copied[inp] = inp_chunk
                graph.add_node(inp_chunk)
            inputs = [inputs_to_copied[inp] for inp in (c.inputs or ())]

            new_op = c.op.copy()
            kws = []
            for o in c.op.outputs:
                kw = dict(_key=o.key, dtype=o.dtype, index=o.index)
                composed = []
                # copy composed
                for j, com in enumerate(o.composed or []):
                    new_com_op = com.op.copy()
                    if j == 0:
                        inps = inputs
                    else:
                        # if more than 1 inputs, means they are exactly the same object
                        inps = [composed[j - 1]] * len(com.inputs)
                    new_com = new_com_op.new_chunk(inps, com.shape, index=com.index,
                                                   dtype=com.dtype, _key=com.key)
                    composed.append(new_com)
                kw['_composed'] = composed
                kws.append(kw)

            new_outputs = new_op.new_chunks(inputs, [o.shape for o in c.op.outputs],
                                            kws=kws)
            for co in new_outputs:
                exec_chunk = co.data
                graph.add_node(exec_chunk)
                for inp in inputs:
                    graph.add_edge(inp, exec_chunk)
        if serialize:
            return serialize_graph(graph)
        else:
            return graph