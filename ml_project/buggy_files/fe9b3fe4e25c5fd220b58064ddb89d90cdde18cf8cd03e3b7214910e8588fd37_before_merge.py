def get_existing(module, args):
    existing = {}
    netcfg = get_config(module)

    try:
        asn_regex = '.*router\sbgp\s(?P<existing_asn>\d+).*'
        match_asn = re.match(asn_regex, str(netcfg), re.DOTALL)
        existing_asn_group = match_asn.groupdict()
        existing_asn = existing_asn_group['existing_asn']
    except AttributeError:
        existing_asn = ''

    if existing_asn:
        bgp_parent = 'router bgp {0}'.format(existing_asn)
        if module.params['vrf'] != 'default':
            parents = [bgp_parent, 'vrf {0}'.format(module.params['vrf'])]
        else:
            parents = [bgp_parent]

        config = netcfg.get_section(parents)
        if config:
            for arg in args:
                if arg != 'asn':
                    if module.params['vrf'] != 'default':
                        if arg not in GLOBAL_PARAMS:
                            existing[arg] = get_value(arg, config)
                    else:
                        existing[arg] = get_value(arg, config)

            existing['asn'] = existing_asn
            if module.params['vrf'] == 'default':
                existing['vrf'] = 'default'
        else:
            if (module.params['state'] == 'present' and
                    module.params['vrf'] != 'default'):
                msg = ("VRF {0} doesn't exist. ".format(module.params['vrf']))
                WARNINGS.append(msg)
    else:
        if (module.params['state'] == 'present' and
                module.params['vrf'] != 'default'):
            msg = ("VRF {0} doesn't exist. ".format(module.params['vrf']))
            WARNINGS.append(msg)

    return existing