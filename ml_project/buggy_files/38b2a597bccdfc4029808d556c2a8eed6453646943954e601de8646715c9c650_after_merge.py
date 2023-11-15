def put_cidr_name(current_config, path, current_path, resource_id, callback_args):
    """Add a display name for all known CIDRs."""

    if 'cidrs' in current_config:
        cidr_list = []
        for cidr in current_config['cidrs']:
            if type(cidr) == dict:
                cidr = cidr['CIDR']
            if cidr in known_cidrs:
                cidr_name = known_cidrs[cidr]
            else:
                cidr_name = get_cidr_name(
                    cidr, callback_args['ip_ranges'], callback_args['ip_ranges_name_key'])
                known_cidrs[cidr] = cidr_name
            cidr_list.append({'CIDR': cidr, 'CIDRName': cidr_name})
        current_config['cidrs'] = cidr_list