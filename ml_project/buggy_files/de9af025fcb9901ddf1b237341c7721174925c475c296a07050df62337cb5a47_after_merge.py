def parse_network(output_layers, extra_layers=None):
    if not isinstance(output_layers, collections.Sequence):
        output_layers = [output_layers]
    if extra_layers is not None:
        if not isinstance(extra_layers, collections.Sequence):
            extra_layers = [extra_layers]
    else:
        extra_layers = []

    layer_names = __get_used_layers__(output_layers + extra_layers)
    submodel_names = __get_used_submodels__(layer_names)
    submodel_names.add('root')
    evaluator_names = __get_used_evaluators__(layer_names)
    input_layer_names = set()
    output_layer_names = set()

    model_config = ModelConfig()
    model_config.type = cp.g_config.model_config.type

    for layer in output_layers:
        model_config.output_layer_names.append(layer.full_name)
        output_layer_names.add(layer.full_name)

    for l in cp.g_config.model_config.layers:
        if l.name not in layer_names:
            continue
        model_config.layers.extend([l])
        if l.type == 'data':
            if l.name in model_config.output_layer_names:
                """
                In text generation, the outlink to save the generated word
                indices is a data_layer defined in recurrent_group. This
                data_layer is sure to be the output of the network in text
                generation task, so this statement excludes such a special
                data_layer from being inputs of the network, otherwise an error
                will occur during data feeding.
                """
                continue
            model_config.input_layer_names.append(l.name)
            input_layer_names.add(l.name)

    for e in cp.g_config.model_config.evaluators:
        if e.name in evaluator_names:
            model_config.evaluators.extend([e])

    for s in cp.g_config.model_config.sub_models:
        if s.name in submodel_names:
            s = __trim_submodel__(s, layer_names, input_layer_names,
                                  output_layer_names, evaluator_names)
            model_config.sub_models.extend([s])

    parameter_names = __get_used_parameters__(layer_names,
                                              model_config.sub_models)

    for p in cp.g_config.model_config.parameters:
        if p.name in parameter_names:
            model_config.parameters.extend([p])

    return model_config