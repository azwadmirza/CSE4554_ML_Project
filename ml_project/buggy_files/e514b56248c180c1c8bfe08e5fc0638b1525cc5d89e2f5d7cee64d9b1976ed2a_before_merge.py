def check_setting_float(config, cfg_name, item_name, def_val=0.0, silent=True):

    if not isinstance(def_val, float):
        logger.log(
            "{dom}:{key} default value is not the correct type. Expected {t}, got {dt}".format(
                dom=cfg_name, key=item_name, t='float', dt=type(def_val)), logger.ERROR)

    try:
        if not (check_section(config, cfg_name) and check_section(config[cfg_name], item_name)):
            raise ValueError

        my_val = float(config[cfg_name][item_name])
    except (ValueError, IndexError, KeyError, TypeError):
        my_val = def_val

        if cfg_name not in config:
            config[cfg_name] = {}

        config[cfg_name][item_name] = my_val

    if not silent:
        logger.log(item_name + " -> " + six.text_type(my_val), logger.DEBUG)

    return my_val