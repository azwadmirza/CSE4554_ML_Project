def unmount_rootfs():
    '''Unmount the filesystem'''
    rootfs_path = os.path.join(constants.temp_folder, constants.mergedir)
    root_command(unmount, '-rl', rootfs_path)