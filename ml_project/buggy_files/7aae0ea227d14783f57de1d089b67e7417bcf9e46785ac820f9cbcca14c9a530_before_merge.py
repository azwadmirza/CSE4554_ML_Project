def begin_parse(config_arg_str=''):
    '''
    @param config_arg_str: a string of the form var1=val1,var2=val2. It will be
    passed to config script as a dictionary CONFIG_ARGS
    '''
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