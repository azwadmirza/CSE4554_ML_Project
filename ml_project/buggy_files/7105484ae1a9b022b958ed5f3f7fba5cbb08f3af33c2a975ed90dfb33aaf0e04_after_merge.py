def _get_gecos(name):
    '''
    Retrieve GECOS field info and return it in dictionary form
    '''
    gecos_field = pwd.getpwnam(name).pw_gecos.split(',', 3)
    if not gecos_field:
        return {}
    else:
        # Assign empty strings for any unspecified trailing GECOS fields
        while len(gecos_field) < 4:
            gecos_field.append('')
        return {'fullname': locales.sdecode(gecos_field[0]),
                'roomnumber': locales.sdecode(gecos_field[1]),
                'workphone': locales.sdecode(gecos_field[2]),
                'homephone': locales.sdecode(gecos_field[3])}