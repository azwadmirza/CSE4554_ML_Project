def parse_config(trainer_config, config_arg_str):
    '''
    @param config_arg_str: a string of the form var1=val1,var2=val2. It will be
    passed to config script as a dictionary CONFIG_ARGS
    '''

    begin_parse()
    config_args = {}

    if config_arg_str:
        config_args = dict([f.split('=') for f in config_arg_str.split(',')])

    global g_command_config_args
    g_command_config_args.update(config_args)

    extension_module_name = config_args.get('extension_module_name')
    if extension_module_name:
        global g_extended_config_funcs
        extension_module = importlib(extension_module_name)
        g_extended_config_funcs = extension_module.get_config_funcs(g_config)

    if hasattr(trainer_config, '__call__'):
        trainer_config.func_globals.update(
            make_config_environment("", config_args))
        trainer_config()
    else:
        execfile(trainer_config,
                 make_config_environment(trainer_config, config_args))

    return update_g_config()