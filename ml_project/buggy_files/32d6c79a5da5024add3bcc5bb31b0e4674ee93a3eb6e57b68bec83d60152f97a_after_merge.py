def execute_image(args):
    """Execution path for container images"""
    logger.debug('Starting analysis...')
    image_string = extract_image(args)
    # If the image has been extracted, load the metadata
    if image_string:
        full_image = cimage.load_full_image(image_string)
        # check if the image was loaded successfully
        if full_image.origins.is_empty():
            # Add an image origin here
            full_image.origins.add_notice_origin(
                formats.docker_image.format(imagetag=image_string))
            # Set up for analysis
            setup(full_image)
            # analyze image
            cimage.analyze(full_image, args.redo, args.driver, args.extend)
            # report out
            report.report_out(args, full_image)
            # clean up
            teardown(full_image)
        else:
            # we cannot load the full image
            logger.error('Cannot retrieve full image metadata')
    # cleanup
    if not args.keep_wd:
        prep.clean_image_tars(full_image)