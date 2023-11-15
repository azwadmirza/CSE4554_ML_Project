def _parse_server_raw(server):
    """Parses a list of server directives.

    :param list server: list of directives in a server block
    :rtype: dict

    """
    parsed_server = {'addrs': set(),
                     'ssl': False,
                     'names': set()}

    apply_ssl_to_all_addrs = False

    for directive in server:
        if not directive:
            continue
        if directive[0] == 'listen':
            addr = obj.Addr.fromstring(directive[1])
            parsed_server['addrs'].add(addr)
            if addr.ssl:
                parsed_server['ssl'] = True
        elif directive[0] == 'server_name':
            parsed_server['names'].update(
                _get_servernames(directive[1]))
        elif directive[0] == 'ssl' and directive[1] == 'on':
            parsed_server['ssl'] = True
            apply_ssl_to_all_addrs = True

    if apply_ssl_to_all_addrs:
        for addr in parsed_server['addrs']:
            addr.ssl = True

    return parsed_server