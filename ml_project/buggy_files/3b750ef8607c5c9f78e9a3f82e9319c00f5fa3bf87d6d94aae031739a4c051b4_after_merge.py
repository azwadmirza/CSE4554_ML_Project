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