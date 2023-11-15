def pull_image(image_tag_string, client):
    """Pull an image from a container registry using Docker
    Note: this function uses the Docker API to pull from a container
    registry and is not responsible for configuring what registry to use"""
    logger.debug("Attempting to pull image \"%s\"", image_tag_string)
    try:
        image = client.images.pull(image_tag_string)
        logger.debug("Image \"%s\" downloaded", image_tag_string)
        return image
    except (docker.errors.ImageNotFound, docker.errors.NotFound):
        logger.warning("No such image: \"%s\"", image_tag_string)
        return None