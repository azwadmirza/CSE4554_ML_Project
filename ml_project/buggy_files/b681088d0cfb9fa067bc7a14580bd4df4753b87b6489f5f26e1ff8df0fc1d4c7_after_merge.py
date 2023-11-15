def metrics_cmd(options, policies):
    log.warning("metrics command is deprecated, and will be removed in future")
    policies = [p for p in policies if p.provider_name == 'aws']
    start, end = _metrics_get_endpoints(options)
    data = {}
    for p in policies:
        log.info('Getting %s metrics', p)
        data[p.name] = p.get_metrics(start, end, options.period)
    print(dumps(data, indent=2))