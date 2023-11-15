def _hw_data(osdata):
    '''
    Get system specific hardware data from dmidecode

    Provides
        biosversion
        productname
        manufacturer
        serialnumber
        biosreleasedate
        uuid

    .. versionadded:: 0.9.5
    '''

    if 'proxyminion' in __opts__:
        return {}

    grains = {}
    if salt.utils.which_bin(['dmidecode', 'smbios']) is not None:
        grains = {
            'biosversion': __salt__['smbios.get']('bios-version'),
            'productname': __salt__['smbios.get']('system-product-name'),
            'manufacturer': __salt__['smbios.get']('system-manufacturer'),
            'biosreleasedate': __salt__['smbios.get']('bios-release-date'),
            'uuid': __salt__['smbios.get']('system-uuid')
        }
        grains = dict([(key, val) for key, val in grains.items() if val is not None])
        uuid = __salt__['smbios.get']('system-uuid')
        if uuid is not None:
            grains['uuid'] = uuid.lower()
        for serial in ('system-serial-number', 'chassis-serial-number', 'baseboard-serial-number'):
            serial = __salt__['smbios.get'](serial)
            if serial is not None:
                grains['serial'] = serial
                break
    elif osdata['kernel'] == 'FreeBSD':
        # On FreeBSD /bin/kenv (already in base system)
        # can be used instead of dmidecode
        kenv = salt.utils.which('kenv')
        if kenv:
            # In theory, it will be easier to add new fields to this later
            fbsd_hwdata = {
                'biosversion': 'smbios.bios.version',
                'manufacturer': 'smbios.system.maker',
                'serialnumber': 'smbios.system.serial',
                'productname': 'smbios.system.product',
                'biosreleasedate': 'smbios.bios.reldate',
                'uuid': 'smbios.system.uuid',
            }
            for key, val in six.iteritems(fbsd_hwdata):
                grains[key] = __salt__['cmd.run']('{0} {1}'.format(kenv, val))
    elif osdata['kernel'] == 'OpenBSD':
        sysctl = salt.utils.which('sysctl')
        hwdata = {'biosversion': 'hw.version',
                  'manufacturer': 'hw.vendor',
                  'productname': 'hw.product',
                  'serialnumber': 'hw.serialno',
                  'uuid': 'hw.uuid'}
        for key, oid in six.iteritems(hwdata):
            value = __salt__['cmd.run']('{0} -n {1}'.format(sysctl, oid))
            if not value.endswith(' value is not available'):
                grains[key] = value
    elif osdata['kernel'] == 'NetBSD':
        sysctl = salt.utils.which('sysctl')
        nbsd_hwdata = {
            'biosversion': 'machdep.dmi.board-version',
            'manufacturer': 'machdep.dmi.system-vendor',
            'serialnumber': 'machdep.dmi.system-serial',
            'productname': 'machdep.dmi.system-product',
            'biosreleasedate': 'machdep.dmi.bios-date',
            'uuid': 'machdep.dmi.system-uuid',
        }
        for key, oid in six.iteritems(nbsd_hwdata):
            result = __salt__['cmd.run_all']('{0} -n {1}'.format(sysctl, oid))
            if result['retcode'] == 0:
                grains[key] = result['stdout']
    elif osdata['kernel'] == 'Darwin':
        grains['manufacturer'] = 'Apple Inc.'
        sysctl = salt.utils.which('sysctl')
        hwdata = {'productname': 'hw.model'}
        for key, oid in hwdata.items():
            value = __salt__['cmd.run']('{0} -b {1}'.format(sysctl, oid))
            if not value.endswith(' is invalid'):
                grains[key] = value

    return grains