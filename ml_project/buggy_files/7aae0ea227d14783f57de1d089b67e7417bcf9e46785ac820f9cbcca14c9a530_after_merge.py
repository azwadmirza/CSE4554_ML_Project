def begin_parse():
    init_config_environment()
    for hook in _parse_config_hooks:
        hook()

    logger.findCaller = find_caller
    logger.fatal = my_fatal

    g_config.model_config.type = "nn"

    global g_current_submodel, g_root_submodel
    g_root_submodel = g_config.model_config.sub_models.add()
    g_root_submodel.name = 'root'
    g_root_submodel.is_recurrent_layer_group = False
    g_current_submodel = g_root_submodel