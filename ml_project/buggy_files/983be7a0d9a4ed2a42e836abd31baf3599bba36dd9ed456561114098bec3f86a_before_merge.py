def _watcher_parser_v2(conf, logname, prom_client):
    logger = config_parser_util.get_logger(logname)
    result = []

    dps = {}
    for faucet_file in conf['faucet_configs']:
        _, dp_list = dp_parser(faucet_file, logname)
        if dp_list:
            for dp in dp_list:
                dps[dp.name] = dp

    dbs = conf.pop('dbs')

    for watcher_name, watcher_conf in list(conf['watchers'].items()):
        watcher_dps = watcher_conf['dps']
        if watcher_conf.get('all_dps', False):
            watcher_dps = list(dps.keys())
        # Watcher config has a list of DPs, but actually a WatcherConf is
        # created for each DP.
        # TODO: refactor watcher_conf as a container.
        for dp_name in watcher_dps:
            if dp_name not in dps:
                logger.error('DP %s in Gauge but not configured in FAUCET', dp_name)
                continue
            dp = dps[dp_name]
            watcher = WatcherConf(watcher_name, dp.dp_id, watcher_conf, prom_client)
            watcher.add_db(dbs[watcher.db])
            watcher.add_dp(dp)
            result.append(watcher)

    return result