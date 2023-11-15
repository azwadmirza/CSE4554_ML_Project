def execute_docker_image(args):
    '''Execution path if given a Docker image'''
    logger.debug('Setting up...')
    image_string = args.docker_image
    if not args.raw_image:
        # don't check docker daemon for raw images
        container.check_docker_setup()
    else:
        image_string = args.raw_image
    report.setup(image_tag_string=image_string)
    # attempt to get built image metadata
    full_image = report.load_full_image(image_string)
    if full_image.origins.is_empty():
        # image loading was successful
        # Add an image origin here
        full_image.origins.add_notice_origin(
            formats.docker_image.format(imagetag=image_string))
        # analyze image
        analyze(full_image, args)
        # generate report
        report.report_out(args, full_image)
    else:
        # we cannot load the full image
        logger.warning('Cannot retrieve full image metadata')
    if not args.keep_wd:
        report.clean_image_tars(full_image)
    logger.debug('Teardown...')
    report.teardown()
    if not args.keep_wd:
        report.clean_working_dir()