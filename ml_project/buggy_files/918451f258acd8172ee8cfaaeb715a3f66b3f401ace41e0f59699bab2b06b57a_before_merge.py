def _gen_xml(name,
             cpu,
             mem,
             diskp,
             nicp,
             hypervisor,
             **kwargs):
    '''
    Generate the XML string to define a libvirt vm
    '''
    hypervisor = 'vmware' if hypervisor == 'esxi' else hypervisor
    mem = mem * 1024  # MB
    data = '''
<domain type='%%HYPERVISOR%%'>
        <name>%%NAME%%</name>
        <vcpu>%%CPU%%</vcpu>
        <memory unit='KiB'>%%MEM%%</memory>
        <os>
                <type>hvm</type>
                %%BOOT%%
        </os>
        <devices>
                %%DISKS%%
                %%CONTROLLER%%
                %%NICS%%
                <graphics type='vnc' listen='0.0.0.0' autoport='yes'/>
                %%SERIAL%%
        </devices>
        <features>
                <acpi/>
        </features>
</domain>
'''
    data = data.replace('%%HYPERVISOR%%', hypervisor)
    data = data.replace('%%NAME%%', name)
    data = data.replace('%%CPU%%', str(cpu))
    data = data.replace('%%MEM%%', str(mem))

    if hypervisor in ['qemu', 'kvm']:
        controller = ''
    elif hypervisor in ['esxi', 'vmware']:
        # TODO: make bus and model parameterized, this works for 64-bit Linux
        controller = '<controller type=\'scsi\' index=\'0\' model=\'lsilogic\'/>'
    data = data.replace('%%CONTROLLER%%', controller)

    boot_str = ''
    if 'boot_dev' in kwargs:
        for dev in kwargs['boot_dev']:
            boot_part = '''<boot dev='%%DEV%%' />
'''
            boot_part = boot_part.replace('%%DEV%%', dev)
            boot_str += boot_part
    else:
        boot_str = '''<boot dev='hd'/>'''
    data = data.replace('%%BOOT%%', boot_str)

    if 'serial_type' in kwargs:
        serial_section = _prepare_serial_port_xml(**kwargs)
    else:
        serial_section = ''
    data = data.replace('%%SERIAL%%', serial_section)

    boot_str = ''
    if 'boot_dev' in kwargs:
        for dev in kwargs['boot_dev']:
            boot_part = "<boot dev='%%DEV%%' />"
            boot_part = boot_part.replace('%%DEV%%', dev)
            boot_str += boot_part
    else:
        boot_str = '''<boot dev='hd'/>'''
    data = data.replace('%%BOOT%%', boot_str)

    disk_t = '''
                <disk type='file' device='disk'>
                        <source %%SOURCE%%/>
                        <target %%TARGET%%/>
                        %%ADDRESS%%
                        %%DRIVER%%
                </disk>
'''
    source = 'file=\'%%SOURCE_FILE%%\''

    if hypervisor in ['qemu', 'kvm']:
        target = 'dev=\'vd%%CHARINDEX%%\' bus=\'%%DISKBUS%%\''
        address = ''
        driver = '<driver name=\'qemu\' type=\'%%DISKTYPE%%\' cache=\'none\' io=\'native\'/>'
    elif hypervisor in ['esxi', 'vmware']:
        target = 'dev=\'sd%%CHARINDEX%%\' bus=\'%%DISKBUS%%\''
        address = '<address type=\'drive\' controller=\'0\' bus=\'0\' target=\'0\' unit=\'%%DISKINDEX%%\'/>'
        driver = ''

    disk_t = disk_t.replace('%%SOURCE%%', source)
    disk_t = disk_t.replace('%%TARGET%%', target)
    disk_t = disk_t.replace('%%ADDRESS%%', address)
    disk_t = disk_t.replace('%%DRIVER%%', driver)
    disk_str = ''
    for i, disk in enumerate(diskp):
        for disk_name, args in disk.items():
            disk_i = disk_t
            file_name = '{0}.{1}'.format(disk_name, args['format'])
            source_file = os.path.join(args['pool'],
                                       name,
                                       file_name)
            disk_i = disk_i.replace('%%SOURCE_FILE%%', source_file)

            disk_i = disk_i.replace('%%CHARINDEX%%', string.ascii_lowercase[i])
            disk_i = disk_i.replace('%%DISKBUS%%', args['model'])

            if '%%DISKTYPE%%' in driver:
                disk_i = disk_i.replace('%%DISKTYPE%%', args['format'])
            if '%%DISKINDEX%%' in address:
                disk_i = disk_i.replace('%%DISKINDEX%%', str(i))
            disk_str += disk_i
    data = data.replace('%%DISKS%%', disk_str)

    nic_str = ''
    for dev, args in nicp.items():
        nic_t = '''
                <interface type='%%TYPE%%'>
                    <source %%SOURCE%%/>
                    <mac address='%%MAC%%'/>
                    <model type='%%MODEL%%'/>
                </interface>
'''
        if 'bridge' in args:
            nic_t = nic_t.replace('%%SOURCE%%', 'bridge=\'{0}\''.format(args['bridge']))
            nic_t = nic_t.replace('%%TYPE%%', 'bridge')
        elif 'network' in args:
            nic_t = nic_t.replace('%%SOURCE%%', 'network=\'{0}\''.format(args['network']))
            nic_t = nic_t.replace('%%TYPE%%', 'network')
        if 'model' in args:
            nic_t = nic_t.replace('%%MODEL%%', args['model'])
        dmac = '{0}_mac'.format(dev)
        if dmac in kwargs:
            nic_t = nic_t.replace('%%MAC%%', kwargs[dmac])
        else:
            nic_t = nic_t.replace('%%MAC%%', salt.utils.gen_mac())
        nic_str += nic_t
    data = data.replace('%%NICS%%', nic_str)
    return data