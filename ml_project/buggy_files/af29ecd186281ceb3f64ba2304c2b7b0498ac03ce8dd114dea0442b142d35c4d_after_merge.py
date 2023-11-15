    def _setup(u, succ):
        if node_name_attribute is not None:
            if node_name_attribute not in tree.nodes[u]:
                raise KeyError(
                    "node '%s' missing node name "
                    "attribute: '%s'"
                    % (u, node_name_attribute))
            node_name = tree.nodes[u][node_name_attribute]
        else:
            node_name = u
        node_to_name[u] = node_name
        m.Nodes.add(node_name)
        if u in succ:
            for v in succ[u]:
                _setup(v, succ)
        else:
            # a leaf node
            if scenario_name_attribute is not None:
                if scenario_name_attribute not in tree.nodes[u]:
                    raise KeyError(
                        "node '%s' missing scenario name "
                        "attribute: '%s'"
                        % (u, scenario_name_attribute))
                scenario_name = tree.nodes[u][scenario_name_attribute]
            else:
                scenario_name = u
            node_to_scenario[u] = scenario_name
            m.Scenarios.add(scenario_name)
            scenario_bundle[scenario_name] = \
                tree.nodes[u].get('bundle', None)