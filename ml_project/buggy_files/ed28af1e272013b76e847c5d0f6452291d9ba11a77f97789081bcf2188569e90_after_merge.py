def pull_image(image_tag_string):
    '''Try to pull an image from Dockerhub'''
    logger.debug("Attempting to pull image \"%s\"", image_tag_string)
    try:
        image = client.images.pull(image_tag_string)
        logger.debug("Image \"%s\" downloaded", image_tag_string)
        return image
    except (docker.errors.ImageNotFound, docker.errors.NotFound):
        logger.warning("No such image: \"%s\"", image_tag_string)
        return None