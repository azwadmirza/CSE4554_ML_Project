def execute_dockerfile(args):
    '''Execution path if given a dockerfile'''
    container.check_docker_setup()
    logger.debug('Setting up...')
    report.setup(dockerfile=args.dockerfile)
    # attempt to build the image
    logger.debug('Building Docker image...')
    # placeholder to check if we can analyze the full image
    completed = True
    build, _ = dhelper.is_build()
    if build:
        # attempt to get built image metadata
        image_tag_string = dhelper.get_dockerfile_image_tag()
        full_image = report.load_full_image(image_tag_string)
        if full_image.origins.is_empty():
            # image loading was successful
            # Add an image origin here
            full_image.origins.add_notice_origin(
                formats.dockerfile_image.format(dockerfile=args.dockerfile))
            # analyze image
            analyze(full_image, args, True)
        else:
            # we cannot load the full image
            logger.warning('Cannot retrieve full image metadata')
            completed = False
        # clean up image
        container.remove_image(full_image.repotag)
        if not args.keep_wd:
            report.clean_image_tars(full_image)
    else:
        # cannot build the image
        logger.warning('Cannot build image')
        completed = False
    # check if we have analyzed the full image or not
    if not completed:
        # get the base image
        logger.debug('Loading base image...')
        base_image = report.load_base_image()
        if base_image.origins.is_empty():
            # image loading was successful
            # add a notice stating failure to build image
            base_image.origins.add_notice_to_origins(
                args.dockerfile, Notice(
                    formats.image_build_failure, 'warning'))
            # analyze image
            analyze(base_image, args)
        else:
            # we cannot load the base image
            logger.warning('Cannot retrieve base image metadata')
        # run through commands in the Dockerfile
        logger.debug('Parsing Dockerfile to generate report...')
        stub_image = get_dockerfile_packages()
        if not args.keep_wd:
            report.clean_image_tars(base_image)
    # generate report based on what images were created
    if completed:
        report.report_out(args, full_image)
    else:
        report.report_out(args, base_image, stub_image)
    logger.debug('Teardown...')
    report.teardown()
    if not args.keep_wd:
        report.clean_working_dir()