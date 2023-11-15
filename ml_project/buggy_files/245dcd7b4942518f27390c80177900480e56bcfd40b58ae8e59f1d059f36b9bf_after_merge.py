def __get_used_layers__(output_layers):
    layer_names = set()
    parents = {}

    def add_parent(child, parent):
        if child in parents:
            parents[child].append(parent)
        else:
            parents[child] = [parent]

    def add_additional_parents():
        for sub_model in cp.g_config.model_config.sub_models:
            if sub_model.name == 'root':
                continue
            for link in sub_model.in_links:
                add_parent(link.link_name, link.layer_name)
                add_parent(sub_model.name, link.layer_name)
            for link in sub_model.out_links:
                add_parent(link.link_name, link.layer_name)
                add_parent(link.link_name, sub_model.name)
            for mem in sub_model.memories:
                if mem.boot_layer_name:
                    add_parent(mem.layer_name, mem.boot_layer_name)
                add_parent(mem.link_name, mem.layer_name)

            if sub_model.HasField('generator'):
                # according to the implementation of text generation
                # in recurrent layer group, the generated word must be
                # the first out link
                add_parent(sub_model.out_links[0].layer_name,
                           sub_model.generator.eos_layer_name)

    def dfs_travel(layer_name):
        if layer_name in layer_names:
            return
        layer_names.add(layer_name)
        layer = cp.g_layer_map[layer_name]

        for inp in layer.inputs:
            dfs_travel(inp.input_layer_name)
        if layer.name in parents:
            for p in parents[layer.name]:
                dfs_travel(p)

    add_additional_parents()

    for layer in output_layers:
        dfs_travel(layer.full_name)

    # print layer needs to be specially handled because no other
    # layer depends on it. It is used to print the result of some
    # layers when running the model for debug purpose. So we explicitly
    # add a print layer to the topolty if its input is in the toplogy.
    for layer in cp.g_config.model_config.layers:
        if layer.type == 'print':
            used = True
            for inp in layer.inputs:
                if inp.input_layer_name not in layer_names:
                    used = False
                    break
            if used:
                layer_names.add(layer.name)

    return layer_names