def get_parameters_for_tree_trav_common(lefts, rights, features, thresholds, values, extra_config={}):
    """
    Common functions used by all tree algorithms to generate the parameters according to the tree_trav strategies.

    Args:
        left: The left nodes
        right: The right nodes
        features: The features used in the decision nodes
        thresholds: The thresholds used in the decision nodes
        values: The values stored in the leaf nodes

    Returns:
        An array containing the extracted parameters
    """
    if len(lefts) == 1:
        # Model creating tree with just a single leaf node. We transform it
        # to a model with one internal node.
        lefts = [1, -1, -1]
        rights = [2, -1, -1]
        features = [0, 0, 0]
        thresholds = [0, 0, 0]
        n_classes = values.shape[1] if type(values) is np.ndarray else 1
        values = np.array([np.zeros(n_classes), values[0], values[0]])
        values.reshape(3, n_classes)

    ids = [i for i in range(len(lefts))]
    nodes = list(zip(ids, lefts, rights, features, thresholds, values))

    # Refactor the tree parameters in the proper format.
    nodes_map = {0: Node(0)}
    current_node = 0
    for i, node in enumerate(nodes):
        id, left, right, feature, threshold, value = node

        if left != -1:
            l_node = Node(left)
            nodes_map[left] = l_node
        else:
            lefts[i] = id
            l_node = -1
            feature = -1

        if right != -1:
            r_node = Node(right)
            nodes_map[right] = r_node
        else:
            rights[i] = id
            r_node = -1
            feature = -1

        nodes_map[current_node].left = l_node
        nodes_map[current_node].right = r_node
        nodes_map[current_node].feature = feature
        nodes_map[current_node].threshold = threshold
        nodes_map[current_node].value = value

        current_node += 1

    lefts = np.array(lefts)
    rights = np.array(rights)
    features = np.array(features)
    thresholds = np.array(thresholds)
    values = np.array(values)

    return [nodes_map, ids, lefts, rights, features, thresholds, values]