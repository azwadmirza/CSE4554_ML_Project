def is_default(interface, module):
    command = 'show run interface {0}'.format(interface)

    try:
        body = run_commands(module, [command], check_rc=False)[0]
        if 'invalid' in body.lower():
            return 'DNE'
        else:
            raw_list = body.split('\n')
            if raw_list[-1].startswith('interface'):
                return True
            else:
                return False
    except (KeyError):
        return 'DNE'