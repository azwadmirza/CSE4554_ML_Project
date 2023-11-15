def to_deeper_graph(graph):
    weighted_layer_ids = graph.deep_layer_ids()
    if len(weighted_layer_ids) >= Constant.MAX_MODEL_DEPTH:
        return None

    deeper_layer_ids = sample(weighted_layer_ids, 1)
    # n_deeper_layer = randint(1, len(weighted_layer_ids))
    # deeper_layer_ids = sample(weighted_layer_ids, n_deeper_layer)

    for layer_id in deeper_layer_ids:
        layer = graph.layer_list[layer_id]
        if is_layer(layer, 'Conv'):
            graph.to_conv_deeper_model(layer_id, randint(1, 2) * 2 + 1)
        else:
            graph.to_dense_deeper_model(layer_id)
    return graph