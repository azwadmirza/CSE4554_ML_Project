def map_config_to_obj(module):
    obj = []

    data = get_config(module, flags=['| section logging'])

    for line in data.split('\n'):
        match = re.search(r'logging (\S+)', line, re.M)

        if match:
            if match.group(1) in DEST_GROUP:
                dest = match.group(1)
                facility = None

                if dest == 'server':
                    facility = parse_facility(line)

            elif match.group(1) == 'level':
                match_facility = re.search(r'logging level (\S+)', line, re.M)
                facility = match_facility.group(1)
                dest = None

            else:
                dest = None
                facility = None

            obj.append({'dest': dest,
                        'remote_server': parse_remote_server(line, dest),
                        'use_vrf': parse_use_vrf(line, dest),
                        'name': parse_name(line, dest),
                        'facility': facility,
                        'dest_level': parse_dest_level(line, dest, parse_name(line, dest)),
                        'facility_level': parse_facility_level(line, facility, dest),
                        'interface_type': parse_interface_type(line),
                        'interface': parse_interface(line)})

    cmd = [{'command': 'show logging | section enabled | section console', 'output': 'text'},
           {'command': 'show logging | section enabled | section monitor', 'output': 'text'}]

    default_data = run_commands(module, cmd)

    for line in default_data:
        flag = False
        match = re.search(r'Logging (\w+):(?:\s+) (?:\w+) (?:\W)Severity: (\w+)', str(line), re.M)
        if match:
            if match.group(1) == 'console' and match.group(2) == 'critical':
                dest_level = '2'
                flag = True
            elif match.group(1) == 'monitor' and match.group(2) == 'notifications':
                dest_level = '5'
                flag = True
        if flag:
            obj.append({'dest': match.group(1),
                        'remote_server': None,
                        'name': None,
                        'facility': None,
                        'dest_level': dest_level,
                        'facility_level': None,
                        'use_vrf': None,
                        'interface_type': None,
                        'interface': None})

    return obj