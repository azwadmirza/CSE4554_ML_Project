    def _add_node(u, stage, succ, pred):
        node_name = node_to_name[u]
        m.NodeStage[node_name] = m.Stages[stage]
        if u == root:
            m.ConditionalProbability[node_name] = 1.0
        else:
            assert u in pred
            # prior to networkx ~2.0, we used a .edge attribute on DiGraph,
            # which no longer exists.
            if hasattr(tree, 'edge'):
                edge = tree.edge[pred[u]][u]
            else:
                edge = tree.edges[pred[u],u]
            probability = None
            if edge_probability_attribute is not None:
                if edge_probability_attribute not in edge:
                    raise KeyError(
                        "edge '(%s, %s)' missing probability attribute: '%s'"
                        % (pred[u], u, edge_probability_attribute))
                probability = edge[edge_probability_attribute]
            else:
                probability = 1.0/len(succ[pred[u]])
            m.ConditionalProbability[node_name] = probability
        # get node variables
        if "variables" in tree.nodes[u]:
            node_variables = tree.nodes[u]["variables"]
            assert type(node_variables) in [tuple, list]
            for varstring in node_variables:
                m.NodeVariables[node_name].add(varstring)
        if "derived_variables" in tree.nodes[u]:
            node_derived_variables = tree.nodes[u]["derived_variables"]
            assert type(node_derived_variables) in [tuple, list]
            for varstring in node_derived_variables:
                m.NodeDerivedVariables[node_name].add(varstring)
        if "cost" in tree.nodes[u]:
            assert isinstance(tree.nodes[u]["cost"], six.string_types)
            m.NodeCost[node_name].value = tree.nodes[u]["cost"]
        if u in succ:
            child_names = []
            for v in succ[u]:
                child_names.append(
                    _add_node(v, stage+1, succ, pred))
            total_probability = 0.0
            for child_name in child_names:
                m.Children[node_name].add(child_name)
                total_probability += \
                    pyomo.core.value(m.ConditionalProbability[child_name])
            if abs(total_probability - 1.0) > 1e-5:
                raise ValueError(
                    "edge probabilities leaving node '%s' "
                    "do not sum to 1 (total=%r)"
                    % (u, total_probability))
        else:
            # a leaf node
            scenario_name = node_to_scenario[u]
            m.ScenarioLeafNode[scenario_name] = node_name
            m.Children[node_name].clear()

        return node_name