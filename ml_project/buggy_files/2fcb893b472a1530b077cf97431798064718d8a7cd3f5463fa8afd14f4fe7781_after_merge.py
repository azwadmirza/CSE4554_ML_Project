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
    for command in ('dmidecode', 'lspci', 'dmesg'):
        args = []
        if osdata['kernel'] == 'Darwin':
            command = 'system_profiler'
            args = ['SPDisplaysDataType']

        cmd = salt.utils.which(command)

        if not cmd:
            continue

        cmd = '%s %s' % (command, ' '.join(args))

        ret = __salt__['cmd.run_all'](cmd)

        if ret['retcode'] > 0:
            if salt.log.is_logging_configured():
                if salt.utils.is_windows():
                    continue
                log.warn(
                    'Although \'{0}\' was found in path, the current user '
                    'cannot execute it. Grains output might not be '
                    'accurate.'.format(command)
                )
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

        elif command == 'dmidecode' or command == 'dmesg':
            # Product Name: VirtualBox
            if 'Vendor: QEMU' in output:
                # FIXME: Make this detect between kvm or qemu
                grains['virtual'] = 'kvm'
            if 'Vendor: Bochs' in output:
                grains['virtual'] = 'kvm'
            # Product Name: (oVirt) www.ovirt.org
            # Red Hat Community virtualization Project based on kvm
            elif 'Manufacturer: oVirt' in output:
                grains['virtual'] = 'kvm'
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
            # Break out of the loop, lspci parsing is not necessary
            break
        elif command == 'lspci':
            # dmidecode not available or the user does not have the necessary
            # permissions
            model = output.lower()
            if 'vmware' in model:
                grains['virtual'] = 'VMware'
            # 00:04.0 System peripheral: InnoTek Systemberatung GmbH VirtualBox Guest Service
            elif 'virtualbox' in model:
                grains['virtual'] = 'VirtualBox'
            elif 'qemu' in model:
                grains['virtual'] = 'kvm'
            elif 'virtio' in model:
                grains['virtual'] = 'kvm'
            # Break out of the loop so the next log message is not issued
            break
    else:
        log.warn(
            'The tools \'dmidecode\', \'lspci\' and \'dmesg\' failed to execute '
            'because they do not exist on the system of the user running '
            'this instance or the user does not have the necessary permissions '
            'to execute them. Grains output might not be accurate.'
        )

    choices = ('Linux', 'OpenBSD', 'HP-UX')
    isdir = os.path.isdir
    sysctl = salt.utils.which('sysctl')
    if osdata['kernel'] in choices:
        if os.path.isfile('/proc/1/cgroup'):
            if ':/lxc/' in salt.utils.fopen('/proc/1/cgroup', 'r').read():
                grains['virtual_subtype'] = 'LXC'
        if isdir('/proc/vz'):
            if os.path.isfile('/proc/vz/version'):
                grains['virtual'] = 'openvzhn'
            else:
                grains['virtual'] = 'openvzve'
        elif isdir('/proc/sys/xen') or isdir('/sys/bus/xen') or isdir('/proc/xen'):
            if os.path.isfile('/proc/xen/xsd_kva'):
                # Tested on CentOS 5.3 / 2.6.18-194.26.1.el5xen
                # Tested on CentOS 5.4 / 2.6.18-164.15.1.el5xen
                grains['virtual_subtype'] = 'Xen Dom0'
            else:
                if grains.get('productname', '') == 'HVM domU':
                    # Requires dmidecode!
                    grains['virtual_subtype'] = 'Xen HVM DomU'
                elif os.path.isfile('/proc/xen/capabilities') and os.access('/proc/xen/capabilities', os.R_OK):
                    caps = salt.utils.fopen('/proc/xen/capabilities')
                    if 'control_d' not in caps.read():
                        # Tested on CentOS 5.5 / 2.6.18-194.3.1.el5xen
                        grains['virtual_subtype'] = 'Xen PV DomU'
                    else:
                        # Shouldn't get to this, but just in case
                        grains['virtual_subtype'] = 'Xen Dom0'
                    caps.close()
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
        if os.path.isfile('/proc/cpuinfo'):
            if 'QEMU Virtual CPU' in salt.utils.fopen('/proc/cpuinfo', 'r').read():
                grains['virtual'] = 'kvm'
    elif osdata['kernel'] == 'FreeBSD':
        kenv = salt.utils.which('kenv')
        if kenv:
            product = __salt__['cmd.run']('{0} smbios.system.product'.format(kenv))
            maker = __salt__['cmd.run']('{0} smbios.system.maker'.format(kenv))
            if product.startswith('VMware'):
                grains['virtual'] = 'VMware'
            if maker.startswith('Xen'):
                grains['virtual_subtype'] = '{0} {1}'.format(maker, product)
                grains['virtual'] = 'xen'
        if sysctl:
            model = __salt__['cmd.run']('{0} hw.model'.format(sysctl))
            jail = __salt__['cmd.run']('{0} -n security.jail.jailed'.format(sysctl))
            if jail == '1':
                grains['virtual_subtype'] = 'jail'
            if 'QEMU Virtual CPU' in model:
                grains['virtual'] = 'kvm'
    elif osdata['kernel'] == 'SunOS':
        # Check if it's a "regular" zone. (i.e. Solaris 10/11 zone)
        zonename = salt.utils.which('zonename')
        if zonename:
            zone = __salt__['cmd.run']('{0}'.format(zonename))
            if zone != 'global':
                grains['virtual'] = 'zone'
                if osdata['os'] == 'SmartOS':
                    grains.update(_smartos_zone_data())
        # Check if it's a branded zone (i.e. Solaris 8/9 zone)
        if isdir('/.SUNWnative'):
            grains['virtual'] = 'zone'
    elif osdata['kernel'] == 'NetBSD':
        if sysctl:
            if 'QEMU Virtual CPU' in __salt__['cmd.run'](
                    '{0} -n machdep.cpu_brand'.format(sysctl)):
                grains['virtual'] = 'kvm'
            elif not 'invalid' in __salt__['cmd.run'](
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

    return grains