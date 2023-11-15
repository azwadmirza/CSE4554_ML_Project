    def _replace_copied_tilebale(self, graph):
        if len(self._optimizer_context) == 0:
            return graph

        new_graph = DAG()
        replaced_tileables = weakref.WeakKeyDictionary()
        for n in graph.topological_iter():
            if graph.count_predecessors(n) == 0:
                if n in self._optimizer_context and \
                        all(suc in self._optimizer_context for suc in graph.successors(n)):
                    replaced_tileables[n] = new_node = self._optimizer_context[n]
                else:
                    new_node = n
            elif any(inp in replaced_tileables for inp in n.inputs) or \
                    any(inp not in new_graph for inp in n.inputs):
                new_inputs = []
                for i in n.inputs:
                    if i in replaced_tileables:
                        new_inputs.append(replaced_tileables[i])
                    elif i not in graph:
                        new_inputs.append(self._optimizer_context[i])
                    else:
                        new_inputs.append(i)
                new_tileables = copy_tileables(n.op.outputs, inputs=new_inputs)
                for t, new_t in zip(n.op.outputs, new_tileables):
                    replaced_tileables[t] = new_t.data
                    if t is n:
                        new_node = new_t.data
            else:
                new_node = n
            new_graph.add_node(new_node)
            for inp in new_node.inputs:
                new_graph.add_node(inp)
                new_graph.add_edge(inp, new_node)
        self._optimizer_context.update(replaced_tileables)
        return new_graph