def prep_rootfs(rootfs_dir):
    '''Mount required filesystems in the rootfs directory'''
    rootfs_path = os.path.abspath(rootfs_dir)
    proc_path = os.path.join(rootfs_path, 'proc')
    sys_path = os.path.join(rootfs_path, 'sys')
    dev_path = os.path.join(rootfs_path, 'dev')
    if not os.path.exists(proc_path):
        os.mkdir(proc_path)
    if not os.path.exists(sys_path):
        os.mkdir(sys_path)
    if not os.path.exists(dev_path):
        os.mkdir(dev_path)
    try:
        root_command(mount_proc, os.path.join(rootfs_path, 'proc'))
        root_command(mount_sys, os.path.join(rootfs_path, 'sys'))
        root_command(mount_dev, os.path.join(rootfs_path, 'dev'))
        root_command(host_dns, os.path.join(
            rootfs_path, constants.resolv_path[1:]))
    except subprocess.CalledProcessError as error:
        logger.error("%s", error.output)
        raise