def _get_gecos(name):
    '''
    Retrieve GECOS field info and return it in dictionary form
    '''
    try:
        gecos_field = pwd.getpwnam(name).pw_gecos.split(',', 3)
    except KeyError:
        raise CommandExecutionError(
            'User \'{0}\' does not exist'.format(name)
        )
    if not gecos_field:
        return {}
    else:
        # Assign empty strings for any unspecified trailing GECOS fields
        while len(gecos_field) < 4:
            gecos_field.append('')
        return {'fullname': str(gecos_field[0]),
                'roomnumber': str(gecos_field[1]),
                'workphone': str(gecos_field[2]),
                'homephone': str(gecos_field[3])}