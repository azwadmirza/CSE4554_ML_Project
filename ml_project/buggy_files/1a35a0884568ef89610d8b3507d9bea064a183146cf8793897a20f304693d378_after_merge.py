def _get_reg_software():
    '''
    This searches the uninstall keys in the registry to find
    a match in the sub keys, it will return a dict with the
    display name as the key and the version as the value
    '''
    ignore_list = ['AddressBook',
                   'Connection Manager',
                   'DirectDrawEx',
                   'Fontcore',
                   'IE40',
                   'IE4Data',
                   'IE5BAKEX',
                   'IEData',
                   'MobileOptionPack',
                   'SchedulingAgent',
                   'WIC',
                   'Not Found',
                   '(value not set)',
                   '',
                   None]
    #encoding = locale.getpreferredencoding()
    reg_software = {}

    hive = 'HKLM'
    key = "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall"

    def update(hive, key, reg_key, use_32bit):

        d_name = ''
        d_vers = ''

        d_name = __salt__['reg.read_value'](hive,
                                            '{0}\\{1}'.format(key, reg_key),
                                            'DisplayName',
                                            use_32bit)['vdata']

        d_vers = __salt__['reg.read_value'](hive,
                                            '{0}\\{1}'.format(key, reg_key),
                                            'DisplayVersion',
                                            use_32bit)['vdata']

        if d_name not in ignore_list:
            # some MS Office updates don't register a product name which means
            # their information is useless
            reg_software.update({d_name: str(d_vers)})

    for reg_key in __salt__['reg.list_keys'](hive, key):
        update(hive, key, reg_key, False)

    for reg_key in __salt__['reg.list_keys'](hive, key, True):
        update(hive, key, reg_key, True)

    return reg_software