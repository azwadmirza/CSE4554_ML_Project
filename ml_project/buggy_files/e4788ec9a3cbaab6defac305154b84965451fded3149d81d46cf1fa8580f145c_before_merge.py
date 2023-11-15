def ScenarioTreeModelFromNetworkX(
        tree,
        node_name_attribute=None,
        edge_probability_attribute='weight',
        stage_names=None,
        scenario_name_attribute=None):
    """
    Create a scenario tree model from a networkx tree.  The
    height of the tree must be at least 1 (meaning at least
    2 stages).

    Required node attributes:
        - cost (str): A string identifying a component on
              the model whose value indicates the cost at
              the time stage of the node for any scenario
              traveling through it.

    Optional node attributes:
        - variables (list): A list of variable identifiers
              that will be tracked by the node. If the node
              is not a leaf node, these indicate variables
              with non-anticipativity constraints.
        - derived_variables (list): A list of variable or
              expression identifiers that will be tracked by
              the node (but will never have
              non-anticipativity constraints enforced).
        - bundle: A bundle identifier for the scenario
              defined by a leaf-stage node. This attribute
              is ignored on non-terminal tree nodes. This
              attribute appears on at least one leaf-stage
              node (and is not set to :const:`None`), then
              it must be set on all leaf-stage nodes (to
              something other than :const:`None`);
              otherwise, an exception will be raised.

    Optional edge attributes:
        - weight (float): Indicates the conditional
              probability of moving from the parent node to
              the child node in the directed edge. If not
              present, it will be assumed that all edges
              leaving the parent node have equal probability
              (normalized to sum to one).

    Args:
        stage_names: Can define a list of stage names to use
           (assumed in time order). The length of this list
           much match the number of stages in the tree. The
           default value of :const:`None` indicates that
           stage names should be automatically generated in
           with the form ['Stage1','Stage2',...].
        node_name_attribute: By default, node names are the
           same as the node hash in the networkx tree. This
           keyword can be set to the name of some property
           of nodes in the graph that will be used for their
           name in the PySP scenario tree.
        scenario_name_attribute: By default, scenario names
           are the same as the leaf-node hash in the
           networkx tree. This keyword can be set to the
           name of some property of leaf-nodes in the graph
           that will be used for their corresponding
           scenario name in the PySP scenario tree.
        edge_probability_attribute: Can be set to the name
           of some property of edges in the graph that
           defines the conditional probability of that
           branch (default: 'weight'). If this keyword is
           set to :const:`None`, then all branches leaving a
           node are assigned equal conditional
           probabilities.

    Examples:

        A 2-stage scenario tree with 10 scenarios grouped
        into 2 bundles:

        >>> G = networkx.DiGraph()
        >>> G.add_node("root", variables=["x"])
        >>> N = 10
        >>> for i in range(N):
        >>>     node_name = "s"+str(i)
        >>>     bundle_name = "b"+str(i%2)
        >>>     G.add_node(node_name, bundle=bundle)
        >>>     G.add_edge("root", node_name, weight=1.0/N)
        >>> model = ScenarioTreeModelFromNetworkX(G)

        A 4-stage scenario tree with 125 scenarios:

        >>> branching_factor = 5
        >>> height = 3
        >>> G = networkx.balanced_tree(
                   branching_factor,
                   height,
                   networkx.DiGraph())
        >>> model = ScenarioTreeModelFromNetworkX(G)
    """

    if not has_networkx:                          #pragma:nocover
        raise ValueError(
            "networkx module is not available")

    if not networkx.is_tree(tree):
        raise TypeError(
            "Graph object is not a tree "
            "(see networkx.is_tree)")

    if not networkx.is_directed(tree):
        raise TypeError(
            "Graph object is not directed "
            "(see networkx.is_directed)")

    if not networkx.is_branching(tree):
        raise TypeError(
            "Grapn object is not a branching "
            "(see networkx.is_branching")

    in_degree_items = tree.in_degree()
    # Prior to networkx ~2.0, in_degree() returned a dictionary.
    # Now it is a view on items, so only call .items() for the old case
    if hasattr(in_degree_items, 'items'):
        in_degree_items = in_degree_items.items()
    root = [u for u,d in in_degree_items if d == 0]
    assert len(root) == 1
    root = root[0]
    num_stages = networkx.eccentricity(tree, v=root) + 1
    if num_stages < 2:
        raise ValueError(
            "The number of stages must be at least 2")
    m = CreateAbstractScenarioTreeModel()
    if stage_names is not None:
        unique_stage_names = set()
        for cnt, stage_name in enumerate(stage_names,1):
            m.Stages.add(stage_name)
            unique_stage_names.add(stage_name)
        if cnt != num_stages:
            raise ValueError(
                "incorrect number of stages names (%s), should be %s"
                % (cnt, num_stages))
        if len(unique_stage_names) != cnt:
            raise ValueError("all stage names were not unique")
    else:
        for i in range(num_stages):
            m.Stages.add('Stage'+str(i+1))
    node_to_name = {}
    node_to_scenario = {}
    scenario_bundle = {}
    def _setup(u, succ):
        if node_name_attribute is not None:
            if node_name_attribute not in tree.node[u]:
                raise KeyError(
                    "node '%s' missing node name "
                    "attribute: '%s'"
                    % (u, node_name_attribute))
            node_name = tree.node[u][node_name_attribute]
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
                if scenario_name_attribute not in tree.node[u]:
                    raise KeyError(
                        "node '%s' missing scenario name "
                        "attribute: '%s'"
                        % (u, scenario_name_attribute))
                scenario_name = tree.node[u][scenario_name_attribute]
            else:
                scenario_name = u
            node_to_scenario[u] = scenario_name
            m.Scenarios.add(scenario_name)
            scenario_bundle[scenario_name] = \
                tree.node[u].get('bundle', None)
    _setup(root,
           networkx.dfs_successors(tree, root))
    m = m.create_instance()
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
        if "variables" in tree.node[u]:
            node_variables = tree.node[u]["variables"]
            assert type(node_variables) in [tuple, list]
            for varstring in node_variables:
                m.NodeVariables[node_name].add(varstring)
        if "derived_variables" in tree.node[u]:
            node_derived_variables = tree.node[u]["derived_variables"]
            assert type(node_derived_variables) in [tuple, list]
            for varstring in node_derived_variables:
                m.NodeDerivedVariables[node_name].add(varstring)
        if "cost" in tree.node[u]:
            assert isinstance(tree.node[u]["cost"], six.string_types)
            m.NodeCost[node_name].value = tree.node[u]["cost"]
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

    _add_node(root,
              1,
              networkx.dfs_successors(tree, root),
              networkx.dfs_predecessors(tree, root))

    if any(_b is not None for _b in scenario_bundle.values()):
        if any(_b is None for _b in scenario_bundle.values()):
            raise ValueError("Incomplete bundle specification. "
                             "All scenarios require a bundle "
                             "identifier.")
        m.Bundling.value = True
        bundle_scenarios = {}
        for bundle_name in sorted(set(scenario_bundle.values())):
            m.Bundles.add(bundle_name)
            bundle_scenarios[bundle_name] = []
        for scenario_name in m.Scenarios:
            bundle_scenarios[scenario_bundle[scenario_name]].\
                append(scenario_name)
        for bundle_name in m.Bundles:
            for scenario_name in sorted(bundle_scenarios[bundle_name]):
                m.BundleScenarios[bundle_name].add(scenario_name)

    return m