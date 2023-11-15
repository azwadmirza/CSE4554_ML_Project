def check_setting_bool(config, cfg_name, item_name, def_val=False, silent=True):
    """
    Checks config setting of boolean type

    :param config: config object
    :type config: ConfigObj()
    :param cfg_name: section name of config
    :param item_name: item name of section
    :param def_val: default value to return in case a value can't be retrieved from config
                    or if couldn't be converted (default: False)
    :param silent: don't log result to debug log (default: True)

    :return: value of `config[cfg_name][item_name]`
             or `def_val` (see cases of def_val)
    :rtype: bool
    """
    try:
        if not isinstance(def_val, bool):
            logger.log(
                "{dom}:{key} default value is not the correct type. Expected {t}, got {dt}".format(
                    dom=cfg_name, key=item_name, t='bool', dt=type(def_val)), logger.ERROR)

        if not (check_section(config, cfg_name) and item_name in config[cfg_name]):
            raise ValueError

        my_val = config[cfg_name][item_name]
        my_val = six.text_type(my_val)
        if my_val == six.text_type(None) or not my_val:
            raise ValueError

        my_val = checkbox_to_value(my_val)
    except (KeyError, IndexError, ValueError):
        my_val = bool(def_val)

        if cfg_name not in config:
            config[cfg_name] = {}

        config[cfg_name][item_name] = my_val

    if not silent:
        logger.log(item_name + " -> " + six.text_type(my_val), logger.DEBUG)

    return my_val