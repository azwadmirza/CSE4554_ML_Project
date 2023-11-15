def check_setting_float(config, cfg_name, item_name, def_val=0.0, min_val=None, max_val=None, fallback_def=True, silent=True):
    """
    Checks config setting of float type

    :param config: config object
    :type config: ConfigObj()
    :param cfg_name: section name of config
    :param item_name: item name of section
    :param def_val: default value to return in case a value can't be retrieved from config
                    or if couldn't be converted,
                    or if `value < min_val` or `value > max_val` (default: 0.0)
    :param min_val: force value to be greater than or equal to `min_val` (optional)
    :param max_val: force value to be lesser than or equal to `max_val` (optional)
    :param fallback_def: if True, `def_val` will be returned when value not in range of `min_val` and `max_val`.
                         otherwise, `min_val`/`max_val` value will be returned respectively (default: True)
    :param silent: don't log result to debug log (default: True)

    :return: value of `config[cfg_name][item_name]` or `min_val`/`max_val` (see def_low_high) `def_val` (see def_val)
    :rtype: float
    """
    if not isinstance(def_val, float):
        logger.log(
            "{dom}:{key} default value is not the correct type. Expected {t}, got {dt}".format(
                dom=cfg_name, key=item_name, t='float', dt=type(def_val)), logger.ERROR)

    if not (min_val is None or isinstance(min_val, float)):
        logger.log(
            "{dom}:{key} min_val value is not the correct type. Expected {t}, got {dt}".format(
                dom=cfg_name, key=item_name, t='float', dt=type(min_val)), logger.ERROR)

    if not (max_val is None or isinstance(max_val, float)):
        logger.log(
            "{dom}:{key} max_val value is not the correct type. Expected {t}, got {dt}".format(
                dom=cfg_name, key=item_name, t='float', dt=type(max_val)), logger.ERROR)

    try:
        if not (check_section(config, cfg_name) and check_section(config[cfg_name], item_name)):
            raise ValueError

        my_val = float(config[cfg_name][item_name])

        if isinstance(min_val, float) and my_val < min_val:
            my_val = config[cfg_name][item_name] = (min_val, def_val)[fallback_def]
        if isinstance(max_val, float) and my_val > max_val:
            my_val = config[cfg_name][item_name] = (max_val, def_val)[fallback_def]
    except (ValueError, IndexError, KeyError, TypeError):
        my_val = def_val

        if cfg_name not in config:
            config[cfg_name] = {}

        config[cfg_name][item_name] = my_val

    if not silent:
        logger.log(item_name + " -> " + six.text_type(my_val), logger.DEBUG)

    return my_val