def _virtual(osdata):
    '''
    Returns what type of virtual hardware is under the hood, kvm or physical
    '''
    # This is going to be a monster, if you are running a vm you can test this
    # grain with please submit patches!
    # Provides:
    #   virtual
    #   virtual_subtype
    grains = {'virtual': 'physical'}

    # Skip the below loop on platforms which have none of the desired cmds
    # This is a temporary measure until we can write proper virtual hardware
    # detection.
    skip_cmds = ('AIX',)

    # list of commands to be executed to determine the 'virtual' grain
    _cmds = ['systemd-detect-virt', 'virt-what', 'dmidecode']
    # test first for virt-what, which covers most of the desired functionality
    # on most platforms
    if not salt.utils.platform.is_windows() and osdata['kernel'] not in skip_cmds:
        if salt.utils.path.which('virt-what'):
            _cmds = ['virt-what']
        else:
            log.debug(
                'Please install \'virt-what\' to improve results of the '
                '\'virtual\' grain.'
            )
    # Check if enable_lspci is True or False
    if __opts__.get('enable_lspci', True) is True:
        # /proc/bus/pci does not exists, lspci will fail
        if os.path.exists('/proc/bus/pci'):
            _cmds += ['lspci']

    # Add additional last resort commands
    if osdata['kernel'] in skip_cmds:
        _cmds = ()

    # Quick backout for BrandZ (Solaris LX Branded zones)
    # Don't waste time trying other commands to detect the virtual grain
    if osdata['kernel'] == 'Linux' and 'BrandZ virtual linux' in os.uname():
        grains['virtual'] = 'zone'
        return grains

    failed_commands = set()
    for command in _cmds:
        args = []
        if osdata['kernel'] == 'Darwin':
            command = 'system_profiler'
            args = ['SPDisplaysDataType']
        elif osdata['kernel'] == 'SunOS':
            virtinfo = salt.utils.path.which('virtinfo')
            if virtinfo:
                try:
                    ret = __salt__['cmd.run_all']('{0} -a'.format(virtinfo))
                except salt.exceptions.CommandExecutionError:
                    if salt.log.is_logging_configured():
                        failed_commands.add(virtinfo)
                else:
                    if ret['stdout'].endswith('not supported'):
                        command = 'prtdiag'
                    else:
                        command = 'virtinfo'
            else:
                command = 'prtdiag'

        cmd = salt.utils.path.which(command)

        if not cmd:
            continue

        cmd = '{0} {1}'.format(cmd, ' '.join(args))

        try:
            ret = __salt__['cmd.run_all'](cmd)

            if ret['retcode'] > 0:
                if salt.log.is_logging_configured():
                    # systemd-detect-virt always returns > 0 on non-virtualized
                    # systems
                    # prtdiag only works in the global zone, skip if it fails
                    if salt.utils.platform.is_windows() or 'systemd-detect-virt' in cmd or 'prtdiag' in cmd:
                        continue
                    failed_commands.add(command)
                continue
        except salt.exceptions.CommandExecutionError:
            if salt.log.is_logging_configured():
                if salt.utils.platform.is_windows():
                    continue
                failed_commands.add(command)
            continue

        output = ret['stdout']
        if command == "system_profiler":
            macoutput = output.lower()
            if '0x1ab8' in macoutput:
                grains['virtual'] = 'Parallels'
            if 'parallels' in macoutput:
                grains['virtual'] = 'Parallels'
            if 'vmware' in macoutput:
                grains['virtual'] = 'VMware'
            if '0x15ad' in macoutput:
                grains['virtual'] = 'VMware'
            if 'virtualbox' in macoutput:
                grains['virtual'] = 'VirtualBox'
            # Break out of the loop so the next log message is not issued
            break
        elif command == 'systemd-detect-virt':
            if output in ('qemu', 'kvm', 'oracle', 'xen', 'bochs', 'chroot', 'uml', 'systemd-nspawn'):
                grains['virtual'] = output
                break
            elif 'vmware' in output:
                grains['virtual'] = 'VMware'
                break
            elif 'microsoft' in output:
                grains['virtual'] = 'VirtualPC'
                break
            elif 'lxc' in output:
                grains['virtual'] = 'LXC'
                break
            elif 'systemd-nspawn' in output:
                grains['virtual'] = 'LXC'
                break
        elif command == 'virt-what':
            if output in ('kvm', 'qemu', 'uml', 'xen', 'lxc'):
                grains['virtual'] = output
                break
            elif 'vmware' in output:
                grains['virtual'] = 'VMware'
                break
            elif 'parallels' in output:
                grains['virtual'] = 'Parallels'
                break
            elif 'hyperv' in output:
                grains['virtual'] = 'HyperV'
                break
        elif command == 'dmidecode':
            # Product Name: VirtualBox
            if 'Vendor: QEMU' in output:
                # FIXME: Make this detect between kvm or qemu
                grains['virtual'] = 'kvm'
            if 'Manufacturer: QEMU' in output:
                grains['virtual'] = 'kvm'
            if 'Vendor: Bochs' in output:
                grains['virtual'] = 'kvm'
            if 'Manufacturer: Bochs' in output:
                grains['virtual'] = 'kvm'
            if 'BHYVE' in output:
                grains['virtual'] = 'bhyve'
            # Product Name: (oVirt) www.ovirt.org
            # Red Hat Community virtualization Project based on kvm
            elif 'Manufacturer: oVirt' in output:
                grains['virtual'] = 'kvm'
                grains['virtual_subtype'] = 'ovirt'
            # Red Hat Enterprise Virtualization
            elif 'Product Name: RHEV Hypervisor' in output:
                grains['virtual'] = 'kvm'
                grains['virtual_subtype'] = 'rhev'
            elif 'VirtualBox' in output:
                grains['virtual'] = 'VirtualBox'
            # Product Name: VMware Virtual Platform
            elif 'VMware' in output:
                grains['virtual'] = 'VMware'
            # Manufacturer: Microsoft Corporation
            # Product Name: Virtual Machine
            elif ': Microsoft' in output and 'Virtual Machine' in output:
                grains['virtual'] = 'VirtualPC'
            # Manufacturer: Parallels Software International Inc.
            elif 'Parallels Software' in output:
                grains['virtual'] = 'Parallels'
            elif 'Manufacturer: Google' in output:
                grains['virtual'] = 'kvm'
            # Proxmox KVM
            elif 'Vendor: SeaBIOS' in output:
                grains['virtual'] = 'kvm'
            # Break out of the loop, lspci parsing is not necessary
            break
        elif command == 'lspci':
            # dmidecode not available or the user does not have the necessary
            # permissions
            model = output.lower()
            if 'vmware' in model:
                grains['virtual'] = 'VMware'
            # 00:04.0 System peripheral: InnoTek Systemberatung GmbH
            #         VirtualBox Guest Service
            elif 'virtualbox' in model:
                grains['virtual'] = 'VirtualBox'
            elif 'qemu' in model:
                grains['virtual'] = 'kvm'
            elif 'virtio' in model:
                grains['virtual'] = 'kvm'
            # Break out of the loop so the next log message is not issued
            break
        elif command == 'prtdiag':
            model = output.lower().split("\n")[0]
            if 'vmware' in model:
                grains['virtual'] = 'VMware'
            elif 'virtualbox' in model:
                grains['virtual'] = 'VirtualBox'
            elif 'qemu' in model:
                grains['virtual'] = 'kvm'
            elif 'joyent smartdc hvm' in model:
                grains['virtual'] = 'kvm'
            break
        elif command == 'virtinfo':
            grains['virtual'] = 'LDOM'
            break
    else:
        if osdata['kernel'] not in skip_cmds:
            log.debug(
                'All tools for virtual hardware identification failed to '
                'execute because they do not exist on the system running this '
                'instance or the user does not have the necessary permissions '
                'to execute them. Grains output might not be accurate.'
            )

    choices = ('Linux', 'HP-UX')
    isdir = os.path.isdir
    sysctl = salt.utils.path.which('sysctl')
    if osdata['kernel'] in choices:
        if os.path.isdir('/proc'):
            try:
                self_root = os.stat('/')
                init_root = os.stat('/proc/1/root/.')
                if self_root != init_root:
                    grains['virtual_subtype'] = 'chroot'
            except (IOError, OSError):
                pass
        if isdir('/proc/vz'):
            if os.path.isfile('/proc/vz/version'):
                grains['virtual'] = 'openvzhn'
            elif os.path.isfile('/proc/vz/veinfo'):
                grains['virtual'] = 'openvzve'
                # a posteriori, it's expected for these to have failed:
                failed_commands.discard('lspci')
                failed_commands.discard('dmidecode')
        # Provide additional detection for OpenVZ
        if os.path.isfile('/proc/self/status'):
            with salt.utils.files.fopen('/proc/self/status') as status_file:
                vz_re = re.compile(r'^envID:\s+(\d+)$')
                for line in status_file:
                    vz_match = vz_re.match(line.rstrip('\n'))
                    if vz_match and int(vz_match.groups()[0]) != 0:
                        grains['virtual'] = 'openvzve'
                    elif vz_match and int(vz_match.groups()[0]) == 0:
                        grains['virtual'] = 'openvzhn'
        if isdir('/proc/sys/xen') or \
                isdir('/sys/bus/xen') or isdir('/proc/xen'):
            if os.path.isfile('/proc/xen/xsd_kva'):
                # Tested on CentOS 5.3 / 2.6.18-194.26.1.el5xen
                # Tested on CentOS 5.4 / 2.6.18-164.15.1.el5xen
                grains['virtual_subtype'] = 'Xen Dom0'
            else:
                if grains.get('productname', '') == 'HVM domU':
                    # Requires dmidecode!
                    grains['virtual_subtype'] = 'Xen HVM DomU'
                elif os.path.isfile('/proc/xen/capabilities') and \
                        os.access('/proc/xen/capabilities', os.R_OK):
                    with salt.utils.files.fopen('/proc/xen/capabilities') as fhr:
                        if 'control_d' not in fhr.read():
                            # Tested on CentOS 5.5 / 2.6.18-194.3.1.el5xen
                            grains['virtual_subtype'] = 'Xen PV DomU'
                        else:
                            # Shouldn't get to this, but just in case
                            grains['virtual_subtype'] = 'Xen Dom0'
                # Tested on Fedora 10 / 2.6.27.30-170.2.82 with xen
                # Tested on Fedora 15 / 2.6.41.4-1 without running xen
                elif isdir('/sys/bus/xen'):
                    if 'xen:' in __salt__['cmd.run']('dmesg').lower():
                        grains['virtual_subtype'] = 'Xen PV DomU'
                    elif os.listdir('/sys/bus/xen/drivers'):
                        # An actual DomU will have several drivers
                        # whereas a paravirt ops kernel will  not.
                        grains['virtual_subtype'] = 'Xen PV DomU'
            # If a Dom0 or DomU was detected, obviously this is xen
            if 'dom' in grains.get('virtual_subtype', '').lower():
                grains['virtual'] = 'xen'
        # Check container type after hypervisors, to avoid variable overwrite on containers running in virtual environment.
        if os.path.isfile('/proc/1/cgroup'):
            try:
                with salt.utils.files.fopen('/proc/1/cgroup', 'r') as fhr:
                    fhr_contents = fhr.read()
                if ':/lxc/' in fhr_contents:
                    grains['virtual_subtype'] = 'LXC'
                else:
                    if any(x in fhr_contents
                           for x in (':/system.slice/docker', ':/docker/',
                                     ':/docker-ce/')):
                        grains['virtual_subtype'] = 'Docker'
            except IOError:
                pass
        if os.path.isfile('/proc/cpuinfo'):
            with salt.utils.files.fopen('/proc/cpuinfo', 'r') as fhr:
                if 'QEMU Virtual CPU' in fhr.read():
                    grains['virtual'] = 'kvm'
        if os.path.isfile('/sys/devices/virtual/dmi/id/product_name'):
            try:
                with salt.utils.files.fopen('/sys/devices/virtual/dmi/id/product_name', 'r') as fhr:
                    output = fhr.read()
                    if 'VirtualBox' in output:
                        grains['virtual'] = 'VirtualBox'
                    elif 'RHEV Hypervisor' in output:
                        grains['virtual'] = 'kvm'
                        grains['virtual_subtype'] = 'rhev'
                    elif 'oVirt Node' in output:
                        grains['virtual'] = 'kvm'
                        grains['virtual_subtype'] = 'ovirt'
                    elif 'Google' in output:
                        grains['virtual'] = 'gce'
                    elif 'BHYVE' in output:
                        grains['virtual'] = 'bhyve'
            except IOError:
                pass
    elif osdata['kernel'] == 'FreeBSD':
        kenv = salt.utils.path.which('kenv')
        if kenv:
            product = __salt__['cmd.run'](
                '{0} smbios.system.product'.format(kenv)
            )
            maker = __salt__['cmd.run'](
                '{0} smbios.system.maker'.format(kenv)
            )
            if product.startswith('VMware'):
                grains['virtual'] = 'VMware'
            if product.startswith('VirtualBox'):
                grains['virtual'] = 'VirtualBox'
            if maker.startswith('Xen'):
                grains['virtual_subtype'] = '{0} {1}'.format(maker, product)
                grains['virtual'] = 'xen'
            if maker.startswith('Microsoft') and product.startswith('Virtual'):
                grains['virtual'] = 'VirtualPC'
            if maker.startswith('OpenStack'):
                grains['virtual'] = 'OpenStack'
            if maker.startswith('Bochs'):
                grains['virtual'] = 'kvm'
        if sysctl:
            hv_vendor = __salt__['cmd.run']('{0} hw.hv_vendor'.format(sysctl))
            model = __salt__['cmd.run']('{0} hw.model'.format(sysctl))
            jail = __salt__['cmd.run'](
                '{0} -n security.jail.jailed'.format(sysctl)
            )
            if 'bhyve' in hv_vendor:
                grains['virtual'] = 'bhyve'
            if jail == '1':
                grains['virtual_subtype'] = 'jail'
            if 'QEMU Virtual CPU' in model:
                grains['virtual'] = 'kvm'
    elif osdata['kernel'] == 'OpenBSD':
        if osdata['manufacturer'] in ['QEMU', 'Red Hat']:
            grains['virtual'] = 'kvm'
        if osdata['manufacturer'] == 'OpenBSD':
            grains['virtual'] = 'vmm'
    elif osdata['kernel'] == 'SunOS':
        if grains['virtual'] == 'LDOM':
            roles = []
            for role in ('control', 'io', 'root', 'service'):
                subtype_cmd = '{0} -c current get -H -o value {1}-role'.format(cmd, role)
                ret = __salt__['cmd.run_all']('{0}'.format(subtype_cmd))
                if ret['stdout'] == 'true':
                    roles.append(role)
            if roles:
                grains['virtual_subtype'] = roles
        else:
            # Check if it's a "regular" zone. (i.e. Solaris 10/11 zone)
            zonename = salt.utils.path.which('zonename')
            if zonename:
                zone = __salt__['cmd.run']('{0}'.format(zonename))
                if zone != 'global':
                    grains['virtual'] = 'zone'
            # Check if it's a branded zone (i.e. Solaris 8/9 zone)
            if isdir('/.SUNWnative'):
                grains['virtual'] = 'zone'
    elif osdata['kernel'] == 'NetBSD':
        if sysctl:
            if 'QEMU Virtual CPU' in __salt__['cmd.run'](
                    '{0} -n machdep.cpu_brand'.format(sysctl)):
                grains['virtual'] = 'kvm'
            elif 'invalid' not in __salt__['cmd.run'](
                    '{0} -n machdep.xen.suspend'.format(sysctl)):
                grains['virtual'] = 'Xen PV DomU'
            elif 'VMware' in __salt__['cmd.run'](
                    '{0} -n machdep.dmi.system-vendor'.format(sysctl)):
                grains['virtual'] = 'VMware'
            # NetBSD has Xen dom0 support
            elif __salt__['cmd.run'](
                    '{0} -n machdep.idle-mechanism'.format(sysctl)) == 'xen':
                if os.path.isfile('/var/run/xenconsoled.pid'):
                    grains['virtual_subtype'] = 'Xen Dom0'

    for command in failed_commands:
        log.info(
            "Although '%s' was found in path, the current user "
            'cannot execute it. Grains output might not be '
            'accurate.', command
        )
    return grains