def map_config_to_obj(module):
    obj = []

    rc, out, err = exec_command(module, 'show ip static route')
    match = re.search(r'.*Static local RIB for default\s*(.*)$', out, re.DOTALL)

    if match and match.group(1):
        for r in match.group(1).splitlines():
            splitted_line = r.split()

            code = splitted_line[0]

            if code != 'M':
                continue

            cidr = ip_network(to_text(splitted_line[1]))
            prefix = str(cidr.network_address)
            mask = str(cidr.netmask)
            next_hop = splitted_line[4]
            admin_distance = splitted_line[2][1]

            obj.append({'prefix': prefix, 'mask': mask,
                        'next_hop': next_hop,
                        'admin_distance': admin_distance})

    return obj