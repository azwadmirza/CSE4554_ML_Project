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

        if state == 'present' and w not in have:
            if w['facility'] is None:
                if w['dest']:
                    if w['dest'] not in ('logfile', 'server'):
                        commands.append('logging {} {}'.format(w['dest'], w['dest_level']))

                    elif w['dest'] == 'logfile':
                        commands.append('logging logfile {} {}'.format(w['name'], w['dest_level']))

                    elif w['dest'] == 'server':
                        if w['dest_level']:
                            commands.append('logging server {0} {1}'.format(
                                w['remote_server'], w['dest_level']))
                        else:
                            commands.append('logging server {0}'.format(w['remote_server']))
                    else:
                        pass

            if w['facility']:
                if w['dest'] == 'server':
                    if w['dest_level']:
                        commands.append('logging server {0} {1} facility {2}'.format(
                            w['remote_server'], w['dest_level'], w['facility']))
                    else:
                        commands.append('logging server {0} facility {1}'.format(w['remote_server'],
                                                                                 w['facility']))
                else:
                    commands.append('logging level {} {}'.format(w['facility'],
                                                                 w['facility_level']))

    return commands