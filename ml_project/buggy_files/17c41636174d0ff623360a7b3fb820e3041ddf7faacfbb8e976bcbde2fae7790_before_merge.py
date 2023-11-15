def unmount_rootfs(num_layers):
    '''Unmount the overlay filesystem'''
    rootfs_path = os.path.join(constants.temp_folder, constants.mergedir)
    for _ in range(num_layers):
        root_command(unmount, '-rl', rootfs_path)