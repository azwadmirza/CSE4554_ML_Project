def get_defined_udas_as_strings(conf, main_section):
    targets = aslist(conf.get(main_section, 'targets'))
    services = set([conf.get(target, 'service') for target in targets])
    uda_list = build_uda_config_overrides(services)

    for uda in convert_override_args_to_taskrc_settings(uda_list):
        yield uda