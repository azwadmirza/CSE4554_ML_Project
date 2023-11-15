def dp_parser(config_file, logname):
    logger = config_parser_util.get_logger(logname)
    conf = config_parser_util.read_config(config_file, logname)
    config_hashes = None
    dps = None

    if conf is not None:
        if type(conf) is dict:
            version = conf.pop('version', 2)
            if version != 2:
                logger.fatal('Only config version 2 is supported')

        else:
            logger.fatal('Config file does not form a dictionary')
            return None, None

        config_hashes, dps = _config_parser_v2(config_file, logname)
    return config_hashes, dps