def map_obj_to_commands(updates):
    commands = list()
    want, have = updates

    for w in want:
        state = w['state']
        del w['state']

        if state == 'absent' and w in have:
            if w['facility'] is not None:
                if not w['dest']:
                    commands.append('no logging level {}'.format(w['facility']))

            if w['name'] is not None:
                commands.append('no logging logfile')

            if w['dest'] in ('console', 'module', 'monitor'):
                commands.append('no logging {}'.format(w['dest']))

            if w['dest'] == 'server':
                commands.append('no logging server {}'.format(w['remote_server']))

            if w['interface_type']:
                commands.append('no logging source-interface')

        if state == 'present' and w not in have:
            if w['facility'] is None:
                if w['dest']:
                    if w['dest'] not in ('logfile', 'server'):
                        commands.append('logging {} {}'.format(w['dest'], w['dest_level']))

                    elif w['dest'] == 'logfile':
                        commands.append('logging logfile {} {}'.format(w['name'], w['dest_level']))

                    elif w['dest'] == 'server':
                        if w['facility_level']:
                            if w['use_vrf']:
                                commands.append('logging server {0} {1} use-vrf {2}'.format(
                                    w['remote_server'], w['facility_level'], w['use_vrf']))
                            else:
                                commands.append('logging server {0} {1}'.format(
                                    w['remote_server'], w['facility_level']))

                        else:
                            if w['use_vrf']:
                                commands.append('logging server {0} use-vrf {1}'.format(
                                    w['remote_server'], w['use_vrf']))
                            else:
                                commands.append('logging server {0}'.format(w['remote_server']))

            if w['facility']:
                if w['dest'] == 'server':
                    if w['facility_level']:
                        if w['use_vrf']:
                            commands.append('logging server {0} {1} facility {2} use-vrf {3}'.format(
                                w['remote_server'], w['facility_level'], w['facility'], w['use_vrf']))
                        else:
                            commands.append('logging server {0} {1} facility {2}'.format(
                                w['remote_server'], w['facility_level'], w['facility']))
                    else:
                        if w['use_vrf']:
                            commands.append('logging server {0} facility {1} use-vrf {2}'.format(
                                w['remote_server'], w['facility'], w['use_vrf']))
                        else:
                            commands.append('logging server {0} facility {1}'.format(w['remote_server'],
                                                                                     w['facility']))
                else:
                    commands.append('logging level {} {}'.format(w['facility'],
                                                                 w['facility_level']))

            if w['interface_type']:
                commands.append('logging source-interface {0} {1}'.format(w['interface_type'],
                                                                          w['interface']))
    return commands