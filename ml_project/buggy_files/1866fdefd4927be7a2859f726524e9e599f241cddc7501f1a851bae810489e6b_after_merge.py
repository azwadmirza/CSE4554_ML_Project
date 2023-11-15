def map_obj_to_commands(updates, module):
    commands = list()
    want, have = updates
    state = module.params['state']

    if state == 'absent' and have.get('text'):
        if isinstance(have['text'], str):
            commands.append('no banner %s' % module.params['banner'])
        elif have['text'].get('loginBanner') or have['text'].get('motd'):
            commands.append({'cmd': 'no banner %s' % module.params['banner']})

    elif state == 'present':
        if isinstance(have['text'], string_types):
            if want['text'] != have['text']:
                commands.append('banner %s' % module.params['banner'])
                commands.extend(want['text'].strip().split('\n'))
                commands.append('EOF')
        else:
            have_text = have['text'].get('loginBanner') or have['text'].get('motd')
            if have_text:
                have_text = have_text.strip()

            if to_text(want['text']) != have_text or not have_text:
                # For EAPI we need to construct a dict with cmd/input
                # key/values for the banner
                commands.append({'cmd': 'banner %s' % module.params['banner'],
                                 'input': want['text'].strip('\n')})

    return commands