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

    if salt.utils.platform.is_proxy():
        return {}

    grains = {}
    if osdata['kernel'] == 'Linux' and os.path.exists('/sys/class/dmi/id'):
        # On many Linux distributions basic firmware information is available via sysfs
        # requires CONFIG_DMIID to be enabled in the Linux kernel configuration
        sysfs_firmware_info = {
            'biosversion': 'bios_version',
            'productname': 'product_name',
            'manufacturer': 'sys_vendor',
            'biosreleasedate': 'bios_date',
            'uuid': 'product_uuid',
            'serialnumber': 'product_serial'
        }
        for key, fw_file in sysfs_firmware_info.items():
            contents_file = os.path.join('/sys/class/dmi/id', fw_file)
            if os.path.exists(contents_file):
                try:
                    with salt.utils.files.fopen(contents_file, 'r') as ifile:
                        grains[key] = ifile.read().strip()
                        if key == 'uuid':
                            grains['uuid'] = grains['uuid'].lower()
                except (IOError, OSError) as err:
                    # PermissionError is new to Python 3, but corresponds to the EACESS and
                    # EPERM error numbers. Use those instead here for PY2 compatibility.
                    if err.errno == EACCES or err.errno == EPERM:
                        # Skip the grain if non-root user has no access to the file.
                        pass
    elif salt.utils.path.which_bin(['dmidecode', 'smbios']) is not None and not (
            salt.utils.platform.is_smartos() or
            (  # SunOS on SPARC - 'smbios: failed to load SMBIOS: System does not export an SMBIOS table'
                osdata['kernel'] == 'SunOS' and
                osdata['cpuarch'].startswith('sparc')
            )):
        # On SmartOS (possibly SunOS also) smbios only works in the global zone
        # smbios is also not compatible with linux's smbios (smbios -s = print summarized)
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
                grains['serialnumber'] = serial
                break
    elif salt.utils.path.which_bin(['fw_printenv']) is not None:
        # ARM Linux devices expose UBOOT env variables via fw_printenv
        hwdata = {
            'manufacturer': 'manufacturer',
            'serialnumber': 'serial#',
        }
        for grain_name, cmd_key in six.iteritems(hwdata):
            result = __salt__['cmd.run_all']('fw_printenv {0}'.format(cmd_key))
            if result['retcode'] == 0:
                uboot_keyval = result['stdout'].split('=')
                grains[grain_name] = _clean_value(grain_name, uboot_keyval[1])
    elif osdata['kernel'] == 'FreeBSD':
        # On FreeBSD /bin/kenv (already in base system)
        # can be used instead of dmidecode
        kenv = salt.utils.path.which('kenv')
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
                value = __salt__['cmd.run']('{0} {1}'.format(kenv, val))
                grains[key] = _clean_value(key, value)
    elif osdata['kernel'] == 'OpenBSD':
        sysctl = salt.utils.path.which('sysctl')
        hwdata = {'biosversion': 'hw.version',
                  'manufacturer': 'hw.vendor',
                  'productname': 'hw.product',
                  'serialnumber': 'hw.serialno',
                  'uuid': 'hw.uuid'}
        for key, oid in six.iteritems(hwdata):
            value = __salt__['cmd.run']('{0} -n {1}'.format(sysctl, oid))
            if not value.endswith(' value is not available'):
                grains[key] = _clean_value(key, value)
    elif osdata['kernel'] == 'NetBSD':
        sysctl = salt.utils.path.which('sysctl')
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
                grains[key] = _clean_value(key, result['stdout'])
    elif osdata['kernel'] == 'Darwin':
        grains['manufacturer'] = 'Apple Inc.'
        sysctl = salt.utils.path.which('sysctl')
        hwdata = {'productname': 'hw.model'}
        for key, oid in hwdata.items():
            value = __salt__['cmd.run']('{0} -b {1}'.format(sysctl, oid))
            if not value.endswith(' is invalid'):
                grains[key] = _clean_value(key, value)
    elif osdata['kernel'] == 'SunOS' and osdata['cpuarch'].startswith('sparc'):
        # Depending on the hardware model, commands can report different bits
        # of information.  With that said, consolidate the output from various
        # commands and attempt various lookups.
        data = ""
        for (cmd, args) in (('/usr/sbin/prtdiag', '-v'), ('/usr/sbin/prtconf', '-vp'), ('/usr/sbin/virtinfo', '-a')):
            if salt.utils.path.which(cmd):  # Also verifies that cmd is executable
                data += __salt__['cmd.run']('{0} {1}'.format(cmd, args))
                data += '\n'

        sn_regexes = [
            re.compile(r) for r in [
                r'(?im)^\s*Chassis\s+Serial\s+Number\n-+\n(\S+)',  # prtdiag
                r'(?im)^\s*chassis-sn:\s*(\S+)',  # prtconf
                r'(?im)^\s*Chassis\s+Serial#:\s*(\S+)',  # virtinfo
            ]
        ]

        obp_regexes = [
            re.compile(r) for r in [
                r'(?im)^\s*System\s+PROM\s+revisions.*\nVersion\n-+\nOBP\s+(\S+)\s+(\S+)',  # prtdiag
                r'(?im)^\s*version:\s*\'OBP\s+(\S+)\s+(\S+)',  # prtconf
            ]
        ]

        fw_regexes = [
            re.compile(r) for r in [
                r'(?im)^\s*Sun\s+System\s+Firmware\s+(\S+)\s+(\S+)',  # prtdiag
            ]
        ]

        uuid_regexes = [
            re.compile(r) for r in [
                r'(?im)^\s*Domain\s+UUID:\s*(\S+)',  # virtinfo
            ]
        ]

        manufacture_regexes = [
            re.compile(r) for r in [
                r'(?im)^\s*System\s+Configuration:\s*(.*)(?=sun)',  # prtdiag
            ]
        ]

        product_regexes = [
            re.compile(r) for r in [
                r'(?im)^\s*System\s+Configuration:\s*.*?sun\d\S+[^\S\r\n]*(.*)',  # prtdiag
                r'(?im)^[^\S\r\n]*banner-name:[^\S\r\n]*(.*)',  # prtconf
                r'(?im)^[^\S\r\n]*product-name:[^\S\r\n]*(.*)',  # prtconf
            ]
        ]

        sn_regexes = [
            re.compile(r) for r in [
                r'(?im)Chassis\s+Serial\s+Number\n-+\n(\S+)',  # prtdiag
                r'(?i)Chassis\s+Serial#:\s*(\S+)',  # virtinfo
                r'(?i)chassis-sn:\s*(\S+)',  # prtconf
            ]
        ]

        obp_regexes = [
            re.compile(r) for r in [
                r'(?im)System\s+PROM\s+revisions.*\nVersion\n-+\nOBP\s+(\S+)\s+(\S+)',  # prtdiag
                r'(?im)version:\s*\'OBP\s+(\S+)\s+(\S+)',  # prtconf
            ]
        ]

        fw_regexes = [
            re.compile(r) for r in [
                r'(?i)Sun\s+System\s+Firmware\s+(\S+)\s+(\S+)',  # prtdiag
            ]
        ]

        uuid_regexes = [
            re.compile(r) for r in [
                r'(?i)Domain\s+UUID:\s+(\S+)',  # virtinfo
            ]
        ]

        for regex in sn_regexes:
            res = regex.search(data)
            if res and len(res.groups()) >= 1:
                grains['serialnumber'] = res.group(1).strip().replace("'", "")
                break

        for regex in obp_regexes:
            res = regex.search(data)
            if res and len(res.groups()) >= 1:
                obp_rev, obp_date = res.groups()[0:2]  # Limit the number in case we found the data in multiple places
                grains['biosversion'] = obp_rev.strip().replace("'", "")
                grains['biosreleasedate'] = obp_date.strip().replace("'", "")

        for regex in fw_regexes:
            res = regex.search(data)
            if res and len(res.groups()) >= 1:
                fw_rev, fw_date = res.groups()[0:2]
                grains['systemfirmware'] = fw_rev.strip().replace("'", "")
                grains['systemfirmwaredate'] = fw_date.strip().replace("'", "")
                break

        for regex in uuid_regexes:
            res = regex.search(data)
            if res and len(res.groups()) >= 1:
                grains['uuid'] = res.group(1).strip().replace("'", "")
                break

        for regex in manufacture_regexes:
            res = regex.search(data)
            if res and len(res.groups()) >= 1:
                grains['manufacture'] = res.group(1).strip().replace("'", "")
                break

        for regex in product_regexes:
            res = regex.search(data)
            if res and len(res.groups()) >= 1:
                t_productname = res.group(1).strip().replace("'", "")
                if t_productname:
                    grains['product'] = t_productname
                    grains['productname'] = t_productname
                    break
    elif osdata['kernel'] == 'AIX':
        cmd = salt.utils.path.which('prtconf')
        if data:
            data = __salt__['cmd.run']('{0}'.format(cmd)) + os.linesep
            for dest, regstring in (('serialnumber', r'(?im)^\s*Machine\s+Serial\s+Number:\s+(\S+)'),
                                    ('systemfirmware', r'(?im)^\s*Firmware\s+Version:\s+(.*)')):
                for regex in [re.compile(r) for r in [regstring]]:
                    res = regex.search(data)
                    if res and len(res.groups()) >= 1:
                        grains[dest] = res.group(1).strip().replace("'", '')

            product_regexes = [re.compile(r'(?im)^\s*System\s+Model:\s+(\S+)')]
            for regex in product_regexes:
                res = regex.search(data)
                if res and len(res.groups()) >= 1:
                    grains['manufacturer'], grains['productname'] = res.group(1).strip().replace("'", "").split(",")
                    break
        else:
            log.error('The \'prtconf\' binary was not found in $PATH.')

    return grains