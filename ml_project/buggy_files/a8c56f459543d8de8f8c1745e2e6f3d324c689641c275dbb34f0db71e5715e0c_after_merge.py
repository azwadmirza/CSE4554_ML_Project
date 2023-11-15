def execute_docker_image(args):
    '''Execution path if given a Docker image'''
    check_docker_daemon()
    logger.debug('Setting up...')
    setup(image_tag_string=args.docker_image)
    # attempt to get built image metadata
    full_image = load_full_image(args.docker_image)
    if full_image.origins.is_empty():
        # image loading was successful
        # Add an image origin here
        full_image.origins.add_notice_origin(
            formats.docker_image.format(imagetag=args.docker_image))
        # analyze image
        analyze_docker_image(full_image)
        # generate report
        generate_report(args, full_image)
    else:
        # we cannot load the full image
        logger.warning('Cannot retrieve full image metadata')
    if not args.keep_working_dir:
        clean_image_tars(full_image)
    logger.debug('Teardown...')
    teardown()
    if not args.keep_working_dir:
        clean_working_dir()