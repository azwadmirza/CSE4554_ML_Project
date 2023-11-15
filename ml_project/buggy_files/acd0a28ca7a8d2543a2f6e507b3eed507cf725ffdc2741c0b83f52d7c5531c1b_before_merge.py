def analyze_docker_image(image_obj, dockerfile=False):
    '''Given a DockerImage object, for each layer, retrieve the packages, first
    looking up in cache and if not there then looking up in the command
    library. For looking up in command library first mount the filesystem
    and then look up the command library for commands to run in chroot'''
    # find the layers that are imported
    if dockerfile:
        docker.set_imported_layers(image_obj)
    # add notices for each layer if it is imported
    for layer in image_obj.layers:
        origin_str = 'Layer: ' + layer.fs_hash[:10]
        layer.origins.add_notice_origin(origin_str)
        if layer.import_str:
            layer.origins.add_notice_to_origins(origin_str, Notice(
                'Imported in Dockerfile using: ' + layer.import_str, 'info'))
    shell = ''
    # set the layer that is mounted. In the beginning this is 0
    mounted = 0
    # set up empty master list of package names
    master_list = []
    # find the shell by mounting the base layer
    target = rootfs.mount_base_layer(image_obj.layers[0].tar_file)
    binary = common.get_base_bin(image_obj.layers[0])
    # find the shell to invoke commands in
    shell, _ = command_lib.get_image_shell(
        command_lib.get_base_listing(binary))
    if not shell:
        shell = constants.shell
    # only extract packages if there is a known binary and the layer is not
    # cached
    if binary:
        if not common.load_from_cache(image_obj.layers[0]):
            # get the packages of the first layer
            rootfs.prep_rootfs(target)
            common.add_base_packages(image_obj.layers[0], binary)
            # unmount proc, sys and dev
            rootfs.undo_mount()
    else:
        logger.warning(errors.unrecognized_base.format(
            image_name=image_obj.name, image_tag=image_obj.tag))
    # populate the master list with all packages found in the first layer
    # can't use assignment as that will just point to the image object's layer
    for p in image_obj.layers[0].get_package_names():
        master_list.append(p)
    # get packages for subsequent layers
    curr_layer = 1
    while curr_layer < len(image_obj.layers):
        if not common.load_from_cache(image_obj.layers[curr_layer]):
            # mount from the layer after the mounted layer till the current
            # layer
            for index in range(mounted + 1, curr_layer + 1):
                target = rootfs.mount_diff_layer(
                    image_obj.layers[index].tar_file)
            mounted = curr_layer
            # mount dev, sys and proc after mounting diff layers
            rootfs.prep_rootfs(target)
            docker.add_packages_from_history(
                image_obj.layers[curr_layer], shell)
            rootfs.undo_mount()
        # update the master list
        common.update_master_list(master_list, image_obj.layers[curr_layer])
        curr_layer = curr_layer + 1
    # undo all the mounts
    rootfs.unmount_rootfs(mounted + 1)
    common.save_to_cache(image_obj)