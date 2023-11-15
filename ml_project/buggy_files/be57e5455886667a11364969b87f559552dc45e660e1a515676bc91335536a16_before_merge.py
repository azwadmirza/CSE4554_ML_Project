def prep_rootfs(rootfs_dir):
    '''Mount required filesystems in the rootfs directory'''
    rootfs_path = os.path.abspath(rootfs_dir)
    try:
        root_command(mount_proc, os.path.join(rootfs_path, 'proc'))
        root_command(mount_sys, os.path.join(rootfs_path, 'sys'))
        root_command(mount_dev, os.path.join(rootfs_path, 'dev'))
        root_command(host_dns, os.path.join(
            rootfs_path, constants.resolv_path[1:]))
    except subprocess.CalledProcessError as error:
        logger.error("%s", error.output)
        raise