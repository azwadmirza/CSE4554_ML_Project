def os_data():
    '''
    Return grains pertaining to the operating system
    '''
    grains = {
        'num_gpus': 0,
        'gpus': [],
    }

    # Windows Server 2008 64-bit
    # ('Windows', 'MINIONNAME', '2008ServerR2', '6.1.7601', 'AMD64', 'Intel64 Fam ily 6 Model 23 Stepping 6, GenuineIntel')
    # Ubuntu 10.04
    # ('Linux', 'MINIONNAME', '2.6.32-38-server', '#83-Ubuntu SMP Wed Jan 4 11:26:59 UTC 2012', 'x86_64', '')
    (grains['kernel'], grains['nodename'],
     grains['kernelrelease'], version, grains['cpuarch'], _) = platform.uname()
    if salt.utils.is_windows():
        grains['osrelease'] = grains['kernelrelease']
        grains['osversion'] = grains['kernelrelease'] = version
        grains['os'] = 'Windows'
        grains['os_family'] = 'Windows'
        grains.update(_memdata(grains))
        grains.update(_windows_platform_data())
        grains.update(_windows_cpudata())
        grains.update(_ps(grains))
        return grains
    elif salt.utils.is_linux():
        # Add lsb grains on any distro with lsb-release
        try:
            import lsb_release
            release = lsb_release.get_distro_information()
            for key, value in release.iteritems():
                key = key.lower()
                lsb_param = 'lsb_{0}{1}'.format(
                    '' if key.startswith('distrib_') else 'distrib_',
                    key
                )
                grains[lsb_param] = value
        except ImportError:
            # if the python library isn't available, default to regex
            if os.path.isfile('/etc/lsb-release'):
                with salt.utils.fopen('/etc/lsb-release') as ifile:
                    for line in ifile:
                        # Matches any possible format:
                        #     DISTRIB_ID="Ubuntu"
                        #     DISTRIB_ID='Mageia'
                        #     DISTRIB_ID=Fedora
                        #     DISTRIB_RELEASE='10.10'
                        #     DISTRIB_CODENAME='squeeze'
                        #     DISTRIB_DESCRIPTION='Ubuntu 10.10'
                        regex = re.compile('^(DISTRIB_(?:ID|RELEASE|CODENAME|DESCRIPTION))=(?:\'|")?([\\w\\s\\.-_]+)(?:\'|")?')
                        match = regex.match(line.rstrip('\n'))
                        if match:
                            # Adds: lsb_distrib_{id,release,codename,description}
                            grains['lsb_{0}'.format(match.groups()[0].lower())] = match.groups()[1].rstrip()
            elif os.path.isfile('/etc/os-release'):
                # Arch ARM Linux
                with salt.utils.fopen('/etc/os-release') as ifile:
                    # Imitate lsb-release
                    for line in ifile:
                        # NAME="Arch Linux ARM"
                        # ID=archarm
                        # ID_LIKE=arch
                        # PRETTY_NAME="Arch Linux ARM"
                        # ANSI_COLOR="0;36"
                        # HOME_URL="http://archlinuxarm.org/"
                        # SUPPORT_URL="https://archlinuxarm.org/forum"
                        # BUG_REPORT_URL="https://github.com/archlinuxarm/PKGBUILDs/issues"
                        regex = re.compile('^([\\w]+)=(?:\'|")?([\\w\\s\\.-_]+)(?:\'|")?')
                        match = regex.match(line.rstrip('\n'))
                        if match:
                            name, value = match.groups()
                            if name.lower() == 'name':
                                grains['lsb_distrib_id'] = value.strip()
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
        # Use the already intelligent platform module to get distro info
        # (though apparently it's not intelligent enough to strip quotes)
        (osname, osrelease, oscodename) = \
            [x.strip('"').strip("'") for x in
             platform.linux_distribution(supported_dists=_supported_dists)]
        # Try to assign these three names based on the lsb info, they tend to
        # be more accurate than what python gets from /etc/DISTRO-release.
        # It's worth noting that Ubuntu has patched their Python distribution
        # so that platform.linux_distribution() does the /etc/lsb-release
        # parsing, but we do it anyway here for the sake for full portability.
        grains['osfullname'] = grains.get('lsb_distrib_id', osname).strip()
        grains['osrelease'] = grains.get('lsb_distrib_release',
                                         osrelease).strip()
        grains['oscodename'] = grains.get('lsb_distrib_codename',
                                          oscodename).strip()
        distroname = _REPLACE_LINUX_RE.sub('', grains['osfullname']).strip()
        # return the first ten characters with no spaces, lowercased
        shortname = distroname.replace(' ', '').lower()[:10]
        # this maps the long names from the /etc/DISTRO-release files to the
        # traditional short names that Salt has used.
        grains['os'] = _OS_NAME_MAP.get(shortname, distroname)
        grains.update(_linux_cpudata())
        grains.update(_linux_gpu_data())
    elif grains['kernel'] == 'SunOS':
        grains['os_family'] = 'Solaris'
        uname_v = __salt__['cmd.run']('uname -v')
        if 'joyent_' in uname_v:
            # See https://github.com/joyent/smartos-live/issues/224
            grains['os'] = grains['osfullname'] = 'SmartOS'
            grains['osrelease'] = uname_v
        elif os.path.isfile('/etc/release'):
            with salt.utils.fopen('/etc/release', 'r') as fp_:
                rel_data = fp_.read()
                try:
                    release_re = r'(Solaris|OpenIndiana(?: Development)?)' \
                                 r'\s+(\d+ \d+\/\d+|oi_\S+)?'
                    osname, osrelease = re.search(release_re,
                                                  rel_data).groups()
                except AttributeError:
                    # Set a blank osrelease grain and fallback to 'Solaris'
                    # as the 'os' grain.
                    grains['os'] = grains['osfullname'] = 'Solaris'
                    grains['osrelease'] = ''
                else:
                    grains['os'] = grains['osfullname'] = osname
                    grains['osrelease'] = osrelease

        grains.update(_sunos_cpudata())
    elif grains['kernel'] == 'VMkernel':
        grains['os'] = 'ESXi'
    elif grains['kernel'] == 'Darwin':
        osrelease = __salt__['cmd.run']('sw_vers -productVersion')
        grains['os'] = 'MacOS'
        grains['osrelease'] = osrelease
        grains.update(_bsd_cpudata(grains))
        grains.update(_osx_gpudata())
    else:
        grains['os'] = grains['kernel']
    if grains['kernel'] in ('FreeBSD', 'OpenBSD', 'NetBSD'):
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

    grains.update(_memdata(grains))

    # Get the hardware and bios data
    grains.update(_hw_data(grains))

    # Load the virtual machine info
    grains.update(_virtual(grains))
    grains.update(_ps(grains))
    if grains['os_family'] == "RedHat":
        grains['osmajorrelease'] = grains['osrelease'].split('.', 1)

    return grains