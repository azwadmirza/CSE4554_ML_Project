def check_setting_str(config, cfg_name, item_name, def_val=six.text_type(''), silent=True, censor_log=False):
    """
    Checks config setting of string types

    :param config: config object
    :type config: ConfigObj()
    :param cfg_name: section name of config
    :param item_name: item name of section
    :param def_val: default value to return in case a value can't be retrieved from config
                    or if couldn't be converted (default: empty six.text_type)
    :param silent: don't log result to debug log (default: True)
    :param censor_log: overrides and adds this setting to logger censored items (default: False)

    :return: decrypted value of `config[cfg_name][item_name]`
             or `def_val` (see cases of def_val)
    :rtype: six.text_type
    """
    if not isinstance(def_val, six.string_types):
        logger.log(
            "{dom}:{key} default value is not the correct type. Expected {t}, got {dt}".format(
                dom=cfg_name, key=item_name, t='string', dt=type(def_val)), logger.ERROR)

    # For passwords you must include the word `password` in the item_name and add `helpers.encrypt(ITEM_NAME, ENCRYPTION_VERSION)` in save_config()
    encryption_version = (0, sickbeard.ENCRYPTION_VERSION)['password' in item_name]

    try:
        if not (check_section(config, cfg_name) and item_name in config[cfg_name]):
            raise ValueError

        my_val = helpers.decrypt(config[cfg_name][item_name], encryption_version)
        if six.text_type(my_val) == six.text_type(None) or not six.text_type(my_val):
            raise ValueError
    except (ValueError, IndexError, KeyError):
        my_val = def_val

        if cfg_name not in config:
            config[cfg_name] = {}

        config[cfg_name][item_name] = helpers.encrypt(my_val, encryption_version)

    if (censor_log or (cfg_name, item_name) in six.iteritems(logger.censored_items)) and not item_name.endswith('custom_url'):
        logger.censored_items[cfg_name, item_name] = my_val

    if not silent:
        logger.log(item_name + " -> " + my_val, logger.DEBUG)

    return six.text_type(my_val)