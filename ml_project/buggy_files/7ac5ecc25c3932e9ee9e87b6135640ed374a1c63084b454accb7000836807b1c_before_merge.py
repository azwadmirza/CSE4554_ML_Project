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