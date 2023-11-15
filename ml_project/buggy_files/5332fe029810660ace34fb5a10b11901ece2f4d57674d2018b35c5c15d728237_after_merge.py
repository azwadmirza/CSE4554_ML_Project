def get_existing(module, args):
    existing = {}
    netcfg = CustomNetworkConfig(indent=2, contents=get_config(module))

    custom = [
        'allowas_in_max',
        'send_community',
        'additional_paths_send',
        'additional_paths_receive',
        'advertise_map_exist',
        'advertise_map_non_exist',
        'filter_list_in',
        'filter_list_out',
        'max_prefix_limit',
        'max_prefix_interval',
        'max_prefix_threshold',
        'max_prefix_warning',
        'next_hop_third_party',
        'prefix_list_in',
        'prefix_list_out',
        'route_map_in',
        'route_map_out',
        'soft_reconfiguration_in'
    ]
    try:
        asn_regex = '.*router\sbgp\s(?P<existing_asn>\d+).*'
        match_asn = re.match(asn_regex, str(netcfg), re.DOTALL)
        existing_asn_group = match_asn.groupdict()
        existing_asn = existing_asn_group['existing_asn']
    except AttributeError:
        existing_asn = ''

    if existing_asn:
        parents = ["router bgp {0}".format(existing_asn)]
        if module.params['vrf'] != 'default':
            parents.append('vrf {0}'.format(module.params['vrf']))

        parents.append('neighbor {0}'.format(module.params['neighbor']))
        parents.append('address-family {0} {1}'.format(
            module.params['afi'], module.params['safi']))
        config = netcfg.get_section(parents)

        if config:
            for arg in args:
                if arg not in ['asn', 'vrf', 'neighbor', 'afi', 'safi']:
                    if arg in custom:
                        existing[arg] = get_custom_value(arg, config, module)
                    else:
                        existing[arg] = get_value(arg, config, module)

            existing['asn'] = existing_asn
            existing['neighbor'] = module.params['neighbor']
            existing['vrf'] = module.params['vrf']
            existing['afi'] = module.params['afi']
            existing['safi'] = module.params['safi']
    else:
        WARNINGS.append("The BGP process didn't exist but the task"
                        " just created it.")

    return existing