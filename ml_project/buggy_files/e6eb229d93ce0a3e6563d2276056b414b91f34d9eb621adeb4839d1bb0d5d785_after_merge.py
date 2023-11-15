def do_main(args):
    '''Execute according to subcommands'''
    # set bind mount location if working in a container
    rootfs.set_mount_dir(args.bind_mount)
    # create working directory
    create_top_dir()
    if args.log_stream:
        # set up console logs
        global logger
        global console
        logger.addHandler(console)
    logger.debug('Starting...')
    if args.clear_cache:
        logger.debug('Clearing cache...')
        cache.clear()
    if hasattr(args, 'name') and args.name == 'report':
        if args.dockerfile:
            run.execute_dockerfile(args)
        if args.docker_image:
            if common.check_tar(args.docker_image):
                logger.error("%s", errors.incorrect_raw_option)
            else:
                run.execute_docker_image(args)
                logger.debug('Report completed.')
        if args.raw_image:
            if not common.check_tar(args.raw_image):
                logger.error("%s", errors.invalid_raw_image.format(
                    image=args.raw_image))
            else:
                run.execute_docker_image(args)
                logger.debug('Report completed.')
    logger.debug('Finished')