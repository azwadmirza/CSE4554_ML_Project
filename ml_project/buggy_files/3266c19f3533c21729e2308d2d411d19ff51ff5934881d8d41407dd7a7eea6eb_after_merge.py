def os_data():
    '''
    Return grains pertaining to the operating system
    '''
    grains = {
        'num_gpus': 0,
        'gpus': [],
        }

    # Windows Server 2008 64-bit
    # ('Windows', 'MINIONNAME', '2008ServerR2', '6.1.7601', 'AMD64',
    #  'Intel64 Fam ily 6 Model 23 Stepping 6, GenuineIntel')
    # Ubuntu 10.04
    # ('Linux', 'MINIONNAME', '2.6.32-38-server',
    # '#83-Ubuntu SMP Wed Jan 4 11:26:59 UTC 2012', 'x86_64', '')

    # pylint: disable=unpacking-non-sequence
    (grains['kernel'], grains['nodename'],
     grains['kernelrelease'], version, grains['cpuarch'], _) = platform.uname()
    # pylint: enable=unpacking-non-sequence

    if salt.utils.is_proxy():
        grains['kernel'] = 'proxy'
        grains['kernelrelease'] = 'proxy'
        grains['osrelease'] = 'proxy'
        grains['os'] = 'proxy'
        grains['os_family'] = 'proxy'
        grains['osfullname'] = 'proxy'
    elif salt.utils.is_windows():
        grains['os'] = 'Windows'
        grains['os_family'] = 'Windows'
        grains.update(_memdata(grains))
        grains.update(_windows_platform_data())
        grains.update(_windows_cpudata())
        grains.update(_windows_virtual(grains))
        grains.update(_ps(grains))

        if 'Server' in grains['osrelease']:
            osrelease_info = grains['osrelease'].split('Server', 1)
            osrelease_info[1] = osrelease_info[1].lstrip('R')
        else:
            osrelease_info = grains['osrelease'].split('.')

        for idx, value in enumerate(osrelease_info):
            if not value.isdigit():
                continue
            osrelease_info[idx] = int(value)
        grains['osrelease_info'] = tuple(osrelease_info)

        grains['osfinger'] = '{os}-{ver}'.format(
            os=grains['os'],
            ver=grains['osrelease'])

        grains['init'] = 'Windows'

        return grains
    elif salt.utils.is_linux():
        # Add SELinux grain, if you have it
        if _linux_bin_exists('selinuxenabled'):
            grains['selinux'] = {}
            grains['selinux']['enabled'] = __salt__['cmd.retcode'](
                'selinuxenabled'
            ) == 0
            if _linux_bin_exists('getenforce'):
                grains['selinux']['enforced'] = __salt__['cmd.run'](
                    'getenforce'
                ).strip()

        # Add systemd grain, if you have it
        if _linux_bin_exists('systemctl') and _linux_bin_exists('localectl'):
            grains['systemd'] = {}
            systemd_info = __salt__['cmd.run'](
                'systemctl --version'
            ).splitlines()
            grains['systemd']['version'] = systemd_info[0].split()[1]
            grains['systemd']['features'] = systemd_info[1]

        # Add init grain
        grains['init'] = 'unknown'
        try:
            os.stat('/run/systemd/system')
            grains['init'] = 'systemd'
        except (OSError, IOError):
            if os.path.exists('/proc/1/cmdline'):
                with salt.utils.fopen('/proc/1/cmdline') as fhr:
                    init_cmdline = fhr.read().replace('\x00', ' ').split()
                    init_bin = salt.utils.which(init_cmdline[0])
                    if init_bin is not None and init_bin.endswith('bin/init'):
                        supported_inits = (six.b('upstart'), six.b('sysvinit'), six.b('systemd'))
                        edge_len = max(len(x) for x in supported_inits) - 1
                        try:
                            buf_size = __opts__['file_buffer_size']
                        except KeyError:
                            # Default to the value of file_buffer_size for the minion
                            buf_size = 262144
                        try:
                            with salt.utils.fopen(init_bin, 'rb') as fp_:
                                buf = True
                                edge = six.b('')
                                buf = fp_.read(buf_size).lower()
                                while buf:
                                    buf = edge + buf
                                    for item in supported_inits:
                                        if item in buf:
                                            if six.PY3:
                                                item = item.decode('utf-8')
                                            grains['init'] = item
                                            buf = six.b('')
                                            break
                                    edge = buf[-edge_len:]
                                    buf = fp_.read(buf_size).lower()
                        except (IOError, OSError) as exc:
                            log.error(
                                'Unable to read from init_bin ({0}): {1}'
                                .format(init_bin, exc)
                            )
                    elif salt.utils.which('supervisord') in init_cmdline:
                        grains['init'] = 'supervisord'
                    elif init_cmdline == ['runit']:
                        grains['init'] = 'runit'
                    else:
                        log.info(
                            'Could not determine init system from command line: ({0})'
                            .format(' '.join(init_cmdline))
                        )

        # Add lsb grains on any distro with lsb-release. Note that this import
        # can fail on systems with lsb-release installed if the system package
        # does not install the python package for the python interpreter used by
        # Salt (i.e. python2 or python3)
        try:
            import lsb_release  # pylint: disable=import-error
            release = lsb_release.get_distro_information()
            for key, value in six.iteritems(release):
                key = key.lower()
                lsb_param = 'lsb_{0}{1}'.format(
                    '' if key.startswith('distrib_') else 'distrib_',
                    key
                )
                grains[lsb_param] = value
        # Catch a NameError to workaround possible breakage in lsb_release
        # See https://github.com/saltstack/salt/issues/37867
        except (ImportError, NameError):
            # if the python library isn't available, default to regex
            if os.path.isfile('/etc/lsb-release'):
                # Matches any possible format:
                #     DISTRIB_ID="Ubuntu"
                #     DISTRIB_ID='Mageia'
                #     DISTRIB_ID=Fedora
                #     DISTRIB_RELEASE='10.10'
                #     DISTRIB_CODENAME='squeeze'
                #     DISTRIB_DESCRIPTION='Ubuntu 10.10'
                regex = re.compile((
                    '^(DISTRIB_(?:ID|RELEASE|CODENAME|DESCRIPTION))=(?:\'|")?'
                    '([\\w\\s\\.\\-_]+)(?:\'|")?'
                ))
                with salt.utils.fopen('/etc/lsb-release') as ifile:
                    for line in ifile:
                        match = regex.match(line.rstrip('\n'))
                        if match:
                            # Adds:
                            #   lsb_distrib_{id,release,codename,description}
                            grains[
                                'lsb_{0}'.format(match.groups()[0].lower())
                            ] = match.groups()[1].rstrip()
            if grains.get('lsb_distrib_description', '').lower().startswith('antergos'):
                # Antergos incorrectly configures their /etc/lsb-release,
                # setting the DISTRIB_ID to "Arch". This causes the "os" grain
                # to be incorrectly set to "Arch".
                grains['osfullname'] = 'Antergos Linux'
            elif 'lsb_distrib_id' not in grains:
                if os.path.isfile('/etc/os-release') or os.path.isfile('/usr/lib/os-release'):
                    os_release = _parse_os_release()
                    if 'NAME' in os_release:
                        grains['lsb_distrib_id'] = os_release['NAME'].strip()
                    if 'VERSION_ID' in os_release:
                        grains['lsb_distrib_release'] = os_release['VERSION_ID']
                    if 'PRETTY_NAME' in os_release:
                        codename = os_release['PRETTY_NAME']
                        # https://github.com/saltstack/salt/issues/44108
                        if os_release['ID'] == 'debian':
                            codename_match = re.search(r'\((\w+)\)$', codename)
                            if codename_match:
                                codename = codename_match.group(1)
                        grains['lsb_distrib_codename'] = codename
                    if 'CPE_NAME' in os_release:
                        if ":suse:" in os_release['CPE_NAME'] or ":opensuse:" in os_release['CPE_NAME']:
                            grains['os'] = "SUSE"
                            # openSUSE `osfullname` grain normalization
                            if os_release.get("NAME") == "openSUSE Leap":
                                grains['osfullname'] = "Leap"
                            elif os_release.get("VERSION") == "Tumbleweed":
                                grains['osfullname'] = os_release["VERSION"]
                elif os.path.isfile('/etc/SuSE-release'):
                    grains['lsb_distrib_id'] = 'SUSE'
                    version = ''
                    patch = ''
                    with salt.utils.fopen('/etc/SuSE-release') as fhr:
                        for line in fhr:
                            if 'enterprise' in line.lower():
                                grains['lsb_distrib_id'] = 'SLES'
                                grains['lsb_distrib_codename'] = re.sub(r'\(.+\)', '', line).strip()
                            elif 'version' in line.lower():
                                version = re.sub(r'[^0-9]', '', line)
                            elif 'patchlevel' in line.lower():
                                patch = re.sub(r'[^0-9]', '', line)
                    grains['lsb_distrib_release'] = version
                    if patch:
                        grains['lsb_distrib_release'] += '.' + patch
                        patchstr = 'SP' + patch
                        if grains['lsb_distrib_codename'] and patchstr not in grains['lsb_distrib_codename']:
                            grains['lsb_distrib_codename'] += ' ' + patchstr
                    if not grains['lsb_distrib_codename']:
                        grains['lsb_distrib_codename'] = 'n.a'
                elif os.path.isfile('/etc/altlinux-release'):
                    # ALT Linux
                    grains['lsb_distrib_id'] = 'altlinux'
                    with salt.utils.fopen('/etc/altlinux-release') as ifile:
                        # This file is symlinked to from:
                        #     /etc/fedora-release
                        #     /etc/redhat-release
                        #     /etc/system-release
                        for line in ifile:
                            # ALT Linux Sisyphus (unstable)
                            comps = line.split()
                            if comps[0] == 'ALT':
                                grains['lsb_distrib_release'] = comps[2]
                                grains['lsb_distrib_codename'] = \
                                    comps[3].replace('(', '').replace(')', '')
                elif os.path.isfile('/etc/centos-release'):
                    # CentOS Linux
                    grains['lsb_distrib_id'] = 'CentOS'
                    with salt.utils.fopen('/etc/centos-release') as ifile:
                        for line in ifile:
                            # Need to pull out the version and codename
                            # in the case of custom content in /etc/centos-release
                            find_release = re.compile(r'\d+\.\d+')
                            find_codename = re.compile(r'(?<=\()(.*?)(?=\))')
                            release = find_release.search(line)
                            codename = find_codename.search(line)
                            if release is not None:
                                grains['lsb_distrib_release'] = release.group()
                            if codename is not None:
                                grains['lsb_distrib_codename'] = codename.group()
                elif os.path.isfile('/etc.defaults/VERSION') \
                        and os.path.isfile('/etc.defaults/synoinfo.conf'):
                    grains['osfullname'] = 'Synology'
                    with salt.utils.fopen('/etc.defaults/VERSION', 'r') as fp_:
                        synoinfo = {}
                        for line in fp_:
                            try:
                                key, val = line.rstrip('\n').split('=')
                            except ValueError:
                                continue
                            if key in ('majorversion', 'minorversion',
                                       'buildnumber'):
                                synoinfo[key] = val.strip('"')
                        if len(synoinfo) != 3:
                            log.warning(
                                'Unable to determine Synology version info. '
                                'Please report this, as it is likely a bug.'
                            )
                        else:
                            grains['osrelease'] = (
                                '{majorversion}.{minorversion}-{buildnumber}'
                                .format(**synoinfo)
                            )

        # Use the already intelligent platform module to get distro info
        # (though apparently it's not intelligent enough to strip quotes)
        (osname, osrelease, oscodename) = \
            [x.strip('"').strip("'") for x in
             linux_distribution(supported_dists=_supported_dists)]
        # Try to assign these three names based on the lsb info, they tend to
        # be more accurate than what python gets from /etc/DISTRO-release.
        # It's worth noting that Ubuntu has patched their Python distribution
        # so that linux_distribution() does the /etc/lsb-release parsing, but
        # we do it anyway here for the sake for full portability.
        if 'osfullname' not in grains:
            grains['osfullname'] = \
                grains.get('lsb_distrib_id', osname).strip()
        if 'osrelease' not in grains:
            # NOTE: This is a workaround for CentOS 7 os-release bug
            # https://bugs.centos.org/view.php?id=8359
            # /etc/os-release contains no minor distro release number so we fall back to parse
            # /etc/centos-release file instead.
            # Commit introducing this comment should be reverted after the upstream bug is released.
            if 'CentOS Linux 7' in grains.get('lsb_distrib_codename', ''):
                grains.pop('lsb_distrib_release', None)
            grains['osrelease'] = \
                grains.get('lsb_distrib_release', osrelease).strip()
        grains['oscodename'] = grains.get('lsb_distrib_codename', '').strip() or oscodename
        if 'Red Hat' in grains['oscodename']:
            grains['oscodename'] = oscodename
        distroname = _REPLACE_LINUX_RE.sub('', grains['osfullname']).strip()
        # return the first ten characters with no spaces, lowercased
        shortname = distroname.replace(' ', '').lower()[:10]
        # this maps the long names from the /etc/DISTRO-release files to the
        # traditional short names that Salt has used.
        if 'os' not in grains:
            grains['os'] = _OS_NAME_MAP.get(shortname, distroname)
        grains.update(_linux_cpudata())
        grains.update(_linux_gpu_data())
    elif grains['kernel'] == 'SunOS':
        if salt.utils.is_smartos():
            # See https://github.com/joyent/smartos-live/issues/224
            uname_v = os.uname()[3]  # format: joyent_20161101T004406Z
            uname_v = uname_v[uname_v.index('_')+1:]
            grains['os'] = grains['osfullname'] = 'SmartOS'
            # store a parsed version of YYYY.MM.DD as osrelease
            grains['osrelease'] = ".".join([
                uname_v.split('T')[0][0:4],
                uname_v.split('T')[0][4:6],
                uname_v.split('T')[0][6:8],
            ])
            # store a untouched copy of the timestamp in osrelease_stamp
            grains['osrelease_stamp'] = uname_v
            if salt.utils.is_smartos_globalzone():
                grains.update(_smartos_computenode_data())
        elif os.path.isfile('/etc/release'):
            with salt.utils.fopen('/etc/release', 'r') as fp_:
                rel_data = fp_.read()
                try:
                    release_re = re.compile(
                        r'((?:Open|Oracle )?Solaris|OpenIndiana|OmniOS) (Development)?'
                        r'\s*(\d+\.?\d*|v\d+)\s?[A-Z]*\s?(r\d+|\d+\/\d+|oi_\S+|snv_\S+)?'
                    )
                    osname, development, osmajorrelease, osminorrelease = \
                        release_re.search(rel_data).groups()
                except AttributeError:
                    # Set a blank osrelease grain and fallback to 'Solaris'
                    # as the 'os' grain.
                    grains['os'] = grains['osfullname'] = 'Solaris'
                    grains['osrelease'] = ''
                else:
                    if development is not None:
                        osname = ' '.join((osname, development))
                    uname_v = os.uname()[3]
                    grains['os'] = grains['osfullname'] = osname
                    if osname in ['Oracle Solaris'] and uname_v.startswith(osmajorrelease):
                        # Oracla Solars 11 and up have minor version in uname
                        grains['osrelease'] = uname_v
                    elif osname in ['OmniOS']:
                        # OmniOS
                        osrelease = []
                        osrelease.append(osmajorrelease[1:])
                        osrelease.append(osminorrelease[1:])
                        grains['osrelease'] = ".".join(osrelease)
                        grains['osrelease_stamp'] = uname_v
                    else:
                        # Sun Solaris 10 and earlier/comparable
                        osrelease = []
                        osrelease.append(osmajorrelease)
                        if osminorrelease:
                            osrelease.append(osminorrelease)
                        grains['osrelease'] = ".".join(osrelease)
                        grains['osrelease_stamp'] = uname_v

        grains.update(_sunos_cpudata())
    elif grains['kernel'] == 'VMkernel':
        grains['os'] = 'ESXi'
    elif grains['kernel'] == 'Darwin':
        osrelease = __salt__['cmd.run']('sw_vers -productVersion')
        osname = __salt__['cmd.run']('sw_vers -productName')
        osbuild = __salt__['cmd.run']('sw_vers -buildVersion')
        grains['os'] = 'MacOS'
        grains['os_family'] = 'MacOS'
        grains['osfullname'] = "{0} {1}".format(osname, osrelease)
        grains['osrelease'] = osrelease
        grains['osbuild'] = osbuild
        grains['init'] = 'launchd'
        grains.update(_bsd_cpudata(grains))
        grains.update(_osx_gpudata())
        grains.update(_osx_platform_data())
    else:
        grains['os'] = grains['kernel']
    if grains['kernel'] == 'FreeBSD':
        try:
            grains['osrelease'] = __salt__['cmd.run']('freebsd-version -u').split('-')[0]
        except salt.exceptions.CommandExecutionError:
            # freebsd-version was introduced in 10.0.
            # derive osrelease from kernelversion prior to that
            grains['osrelease'] = grains['kernelrelease'].split('-')[0]
        grains.update(_bsd_cpudata(grains))
    if grains['kernel'] in ('OpenBSD', 'NetBSD'):
        grains.update(_bsd_cpudata(grains))
        grains['osrelease'] = grains['kernelrelease'].split('-')[0]
        if grains['kernel'] == 'NetBSD':
            grains.update(_netbsd_gpu_data())
    if not grains['os']:
        grains['os'] = 'Unknown {0}'.format(grains['kernel'])
        grains['os_family'] = 'Unknown'
    else:
        # this assigns family names based on the os name
        # family defaults to the os name if not found
        grains['os_family'] = _OS_FAMILY_MAP.get(grains['os'],
                                                 grains['os'])

    # Build the osarch grain. This grain will be used for platform-specific
    # considerations such as package management. Fall back to the CPU
    # architecture.
    if grains.get('os_family') == 'Debian':
        osarch = __salt__['cmd.run']('dpkg --print-architecture').strip()
    elif grains.get('os_family') == 'RedHat':
        osarch = __salt__['cmd.run']('rpm --eval %{_host_cpu}').strip()
    elif grains.get('os_family') == 'NILinuxRT':
        archinfo = {}
        for line in __salt__['cmd.run']('opkg print-architecture').splitlines():
            if line.startswith('arch'):
                _, arch, priority = line.split()
                archinfo[arch.strip()] = int(priority.strip())

        # Return osarch in priority order (higher to lower)
        osarch = sorted(archinfo, key=archinfo.get, reverse=True)
    else:
        osarch = grains['cpuarch']
    grains['osarch'] = osarch

    grains.update(_memdata(grains))

    # Get the hardware and bios data
    grains.update(_hw_data(grains))

    # Get zpool data
    grains.update(_zpool_data(grains))

    # Load the virtual machine info
    grains.update(_virtual(grains))
    grains.update(_ps(grains))

    if grains.get('osrelease', ''):
        osrelease_info = grains['osrelease'].split('.')
        for idx, value in enumerate(osrelease_info):
            if not value.isdigit():
                continue
            osrelease_info[idx] = int(value)
        grains['osrelease_info'] = tuple(osrelease_info)
        try:
            grains['osmajorrelease'] = int(grains['osrelease_info'][0])
        except (IndexError, TypeError, ValueError):
            log.debug(
                'Unable to derive osmajorrelease from osrelease_info \'%s\'. '
                'The osmajorrelease grain will not be set.',
                grains['osrelease_info']
            )
        os_name = grains['os' if grains.get('os') in (
            'FreeBSD', 'OpenBSD', 'NetBSD', 'Mac', 'Raspbian') else 'osfullname']
        grains['osfinger'] = '{0}-{1}'.format(
            os_name, grains['osrelease'] if os_name in ('Ubuntu',) else grains['osrelease_info'][0])

    return grains