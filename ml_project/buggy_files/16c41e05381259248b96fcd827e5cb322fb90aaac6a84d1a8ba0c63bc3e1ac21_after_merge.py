def full_image_analysis(dfile, redo, driver, keep, extension):
    """This subroutine is executed when a Dockerfile is successfully built"""
    image_list = []
    # attempt to load the built image metadata
    full_image = cimage.load_full_image(dfile)
    if full_image.origins.is_empty():
        # Add an image origin here
        full_image.origins.add_notice_origin(
            formats.dockerfile_image.format(dockerfile=dfile))
        image_list = analyze_full_image(full_image, redo, driver, extension)
    else:
        # we cannot analyze the full image, but maybe we can
        # analyze the base image
        logger.error('Cannot retrieve full image metadata')
    # cleanup for full images
    if not keep:
        prep.clean_image_tars(full_image)
    return image_list