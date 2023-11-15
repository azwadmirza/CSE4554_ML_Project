    def resolve_stack_topology(self, dps):
        """Resolve inter-DP config for stacking."""
        root_dp = None
        stack_dps = []
        for dp in dps:
            if dp.stack is not None:
                stack_dps.append(dp)
                if 'priority' in dp.stack:
                    test_config_condition(dp.stack['priority'] <= 0, (
                        'stack priority must be > 0'))
                    test_config_condition(root_dp is not None, 'cannot have multiple stack roots')
                    root_dp = dp
                    for vlan in dp.vlans.values():
                        test_config_condition(vlan.faucet_vips, (
                            'routing + stacking not supported'))

        if root_dp is None:
            test_config_condition(stack_dps, 'stacking enabled but no root_dp')
            return

        edge_count = Counter()

        graph = networkx.MultiGraph()
        for dp in dps:
            if dp.stack_ports:
                graph.add_node(dp.name)
                for port in dp.stack_ports:
                    edge_name = self.add_stack_link(graph, dp, port)
                    edge_count[edge_name] += 1
        if graph.size():
            for edge_name, count in edge_count.items():
                test_config_condition(count != 2, '%s defined only in one direction' % edge_name)
            if self.name in graph:
                if self.stack is None:
                    self.stack = {}
                self.stack['root_dp'] = root_dp
                self.stack['graph'] = graph
                longest_path_to_root_len = 0
                for dp in graph.nodes():
                    path_to_root_len = len(self.shortest_path(root_dp.name, src_dp=dp))
                    test_config_condition(
                        path_to_root_len == 0, '%s not connected to stack' % dp)
                    longest_path_to_root_len = max(
                        path_to_root_len, longest_path_to_root_len)
                self.stack['longest_path_to_root_len'] = longest_path_to_root_len