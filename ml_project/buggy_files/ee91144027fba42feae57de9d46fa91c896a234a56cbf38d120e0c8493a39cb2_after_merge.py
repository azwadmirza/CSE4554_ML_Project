    def _return_from_call(self, from_func, to_node, to_outside=False):
        self.transition_graph.add_edge(from_func, to_node, type='return', to_outside=to_outside)
        for _, _, data in self.transition_graph.in_edges(to_node, data=True):
            if 'type' in data and data['type'] == 'fake_return':
                data['confirmed'] = True

        self._local_transition_graph = None