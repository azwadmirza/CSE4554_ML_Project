def analyze_docker_image(image_obj, redo=False, dockerfile=False):
    '''Given a DockerImage object, for each layer, retrieve the packages, first
    looking up in cache and if not there then looking up in the command
    library. For looking up in command library first mount the filesystem
    and then look up the command library for commands to run in chroot'''
    # find the layers that are imported
    if dockerfile:
        docker.set_imported_layers(image_obj)
    # add notices for each layer if it is imported
    image_setup(image_obj)
    shell = ''
    # set up empty master list of packages
    master_list = []
    # find the binary by mounting the base layer
    target = rootfs.mount_base_layer(image_obj.layers[0].tar_file)
    binary = common.get_base_bin(image_obj.layers[0])
    # set up a notice origin referring to the base command library listing
    origin_command_lib = formats.invoking_base_commands
    # set up a notice origin for the first layer
    origin_first_layer = 'Layer: ' + image_obj.layers[0].fs_hash[:10]
    # find the shell to invoke commands in
    shell, msg = command_lib.get_image_shell(
        command_lib.get_base_listing(binary))
    if not shell:
        # add a warning notice for no shell in the command library
        logger.warning('No shell listing in command library. '
                       'Using default shell')
        no_shell_message = errors.no_shell_listing.format(
            binary=binary, default_shell=constants.shell)
        image_obj.layers[0].origins.add_notice_to_origins(
            origin_command_lib, Notice(no_shell_message, 'warning'))
        # add a hint notice to add the shell to the command library
        add_shell_message = errors.no_listing_for_base_key.format(
            listing_key='shell')
        image_obj.layers[0].origins.add_notice_to_origins(
            origin_command_lib, Notice(add_shell_message, 'hint'))
        shell = constants.shell
    # only extract packages if there is a known binary and the layer is not
    # cached
    if binary:
        if not common.load_from_cache(image_obj.layers[0], redo):
            # get the packages of the first layer
            rootfs.prep_rootfs(target)
            common.add_base_packages(image_obj.layers[0], binary, shell)
            # unmount proc, sys and dev
            rootfs.undo_mount()
    else:
        no_base = errors.unrecognized_base.format(
            image_name=image_obj.name, image_tag=image_obj.tag)
        logger.warning(no_base)
        image_obj.layers[0].origins.add_notice_to_origins(
            origin_first_layer, Notice(no_base, 'warning'))
        # no binary means there is no shell so set to default shell
        logger.warning('Unknown filesystem. Using default shell')
        shell = constants.shell
    # unmount the first layer
    rootfs.unmount_rootfs()
    # populate the master list with all packages found in the first layer
    for p in image_obj.layers[0].packages:
        master_list.append(p)
    # get packages for subsequent layers
    curr_layer = 1
    while curr_layer < len(image_obj.layers):
        if not common.load_from_cache(image_obj.layers[curr_layer], redo):
            # get commands that created the layer
            # for docker images this is retrieved from the image history
            command_list = docker.get_commands_from_history(
                image_obj.layers[curr_layer])
            if command_list:
                # mount diff layers from 0 till the current layer
                mount_overlay_fs(image_obj, curr_layer)
            # for each command look up the snippet library
            for command in command_list:
                pkg_listing = command_lib.get_package_listing(command.name)
                if type(pkg_listing) is str:
                    common.add_base_packages(
                        image_obj.layers[curr_layer], pkg_listing, shell)
                else:
                    common.add_snippet_packages(
                        image_obj.layers[curr_layer], command, pkg_listing,
                        shell)
            if command_list:
                rootfs.undo_mount()
                rootfs.unmount_rootfs()
        # update the master list
        common.update_master_list(master_list, image_obj.layers[curr_layer])
        curr_layer = curr_layer + 1
    common.save_to_cache(image_obj)