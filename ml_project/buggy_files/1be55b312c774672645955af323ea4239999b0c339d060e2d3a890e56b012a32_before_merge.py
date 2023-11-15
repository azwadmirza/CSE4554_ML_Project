def init(name,
         cpu,
         mem,
         image=None,
         nic='default',
         hypervisor=VIRT_DEFAULT_HYPER,
         start=True,
         disk='default',
         **kwargs):
    '''
    Initialize a new vm

    CLI Example:

    .. code-block:: bash

        salt 'hypervisor' virt.init vm_name 4 512 salt://path/to/image.raw
        salt 'hypervisor' virt.init vm_name 4 512 nic=profile disk=profile
    '''
    hypervisor = __salt__['config.get']('libvirt:hypervisor', hypervisor)
    nicp = _nic_profile(nic, hypervisor)
    diskp = None
    seedable = False
    if image:  # with disk template image
        # if image was used, assume only one disk, i.e. the
        # 'default' disk profile
        # TODO: make it possible to use disk profiles and use the
        # template image as the system disk
        diskp = _disk_profile('default', hypervisor, **kwargs)

        # When using a disk profile extract the sole dict key of the first
        # array element as the filename for disk
        disk_name = diskp[0].keys()[0]
        disk_type = diskp[0][disk_name]['format']
        disk_file_name = '{0}.{1}'.format(disk_name, disk_type)

        if hypervisor in ['esxi', 'vmware']:
            # TODO: we should be copying the image file onto the ESX host
            raise SaltInvocationError('virt.init does not support image '
                                      'template template in conjunction '
                                      'with esxi hypervisor')
        elif hypervisor in ['qemu', 'kvm']:
            img_dir = __salt__['config.option']('virt.images')
            img_dest = os.path.join(
                img_dir,
                name,
                disk_file_name
            )
            img_dir = os.path.dirname(img_dest)
            sfn = __salt__['cp.cache_file'](image)
            if not os.path.isdir(img_dir):
                os.makedirs(img_dir)
            salt.utils.copyfile(sfn, img_dest)
            seedable = True
        else:
            log.error('unsupported hypervisor when handling disk image')

    else:
        # no disk template image specified, create disks based on disk profile
        diskp = _disk_profile(disk, hypervisor, **kwargs)
        if hypervisor in ['qemu', 'kvm']:
            # TODO: we should be creating disks in the local filesystem with
            # qemu-img
            raise SaltInvocationError('virt.init does not support disk '
                                      'profiles in conjunction with '
                                      'qemu/kvm at this time, use image '
                                      'template instead')
        else:
            # assume libvirt manages disks for us
            for disk in diskp:
                for disk_name, args in disk.items():
                    xml = _gen_vol_xml(name,
                                       disk_name,
                                       args['size'],
                                       hypervisor)
                    define_vol_xml_str(xml)

    xml = _gen_xml(name, cpu, mem, diskp, nicp, hypervisor, **kwargs)
    define_xml_str(xml)

    if kwargs.get('seed') and seedable:
        install = kwargs.get('install', True)
        __salt__['seed.apply'](img_dest,
                               id_=name,
                               config=kwargs.get('config'),
                               install=install)
    elif kwargs.get('seed_cmd') and seedable:
        __salt__[kwargs['seed_cmd']](img_dest, name, kwargs.get('config'))
    if start:
        create(name)

    return True