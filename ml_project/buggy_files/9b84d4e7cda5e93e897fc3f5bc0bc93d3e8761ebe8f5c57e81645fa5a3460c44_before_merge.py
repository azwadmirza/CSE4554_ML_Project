def beacon(config):
    '''
    Watch for changes on network settings

    By default, the beacon will emit when there is a value change on one of the
    settings on watch. The config also support the onvalue parameter for each
    setting, which instruct the beacon to only emit if the setting changed to
    the value defined.

    Example Config

    .. code-block:: yaml

        beacons:
          network_settings:
            - interfaces:
                eth0:
                  ipaddr:
                  promiscuity:
                    onvalue: 1
                eth1:
                  linkmode:

    The config above will check for value changes on eth0 ipaddr and eth1 linkmode. It will also
    emit if the promiscuity value changes to 1.

    Beacon items can use the * wildcard to make a definition apply to several interfaces. For
    example an eth* would apply to all ethernet interfaces.

    Setting the argument coalesce = True will combine all the beacon results on a single event.
    The example below shows how to trigger coalesced results:

    .. code-block:: yaml

        beacons:
          network_settings:
            - coalesce: True
            - interfaces:
                eth0:
                  ipaddr:
                  promiscuity:

    '''
    _config = {}
    list(map(_config.update, config))

    ret = []
    interfaces = []
    expanded_config = {}

    global LAST_STATS

    coalesce = False

    _stats = _copy_interfaces_info(IP.by_name)

    if not LAST_STATS:
        LAST_STATS = _stats

    if 'coalesce' in _config and _config['coalesce']:
        coalesce = True
        changes = {}

    log.debug('_stats %s', _stats)
    # Get list of interfaces included in config that are registered in the
    # system, including interfaces defined by wildcards (eth*, wlan*)
    for interface in _config.get('interfaces', {}):
        if interface in _stats:
            interfaces.append(interface)
        else:
            # No direct match, try with * wildcard regexp
            interface_regexp = interface.replace('*', '[0-9]+')
            for interface in _stats:
                match = re.search(interface_regexp, interface)
                if match:
                    interfaces.append(match.group())
                    expanded_config[match.group()] = config['interfaces'][interface]

    if expanded_config:
        config.update(expanded_config)

        # config updated so update _config
        list(map(_config.update, config))

    log.debug('interfaces %s', interfaces)
    for interface in interfaces:
        _send_event = False
        _diff_stats = _stats[interface] - LAST_STATS[interface]
        _ret_diff = {}
        interface_config = _config['interfaces'][interface]

        log.debug('_diff_stats %s', _diff_stats)
        if _diff_stats:
            _diff_stats_dict = {}
            LAST_STATS[interface] = _stats[interface]

            for item in _diff_stats:
                _diff_stats_dict.update(item)
            for attr in interface_config:
                if attr in _diff_stats_dict:
                    config_value = None
                    if interface_config[attr] and \
                       'onvalue' in interface_config[attr]:
                        config_value = interface_config[attr]['onvalue']
                    new_value = ast.literal_eval(_diff_stats_dict[attr])
                    if not config_value or config_value == new_value:
                        _send_event = True
                        _ret_diff[attr] = new_value

            if _send_event:
                if coalesce:
                    changes[interface] = _ret_diff
                else:
                    ret.append({'tag': interface,
                                'interface': interface,
                                'change': _ret_diff})

    if coalesce and changes:
        grains_info = salt.loader.grains(__opts__, True)
        __grains__.update(grains_info)
        ret.append({'tag': 'result', 'changes': changes})

    return ret