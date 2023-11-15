def dump_docker_image(image_tag):
    """Given an image and tag or image and digest, use the Docker API to get
    a container image representation into the working directory"""
    image_metadata = None
    # open up a client first
    # if this fails we cannot proceed further so we will exit
    client = check_docker_setup()
    image = get_docker_image(image_tag, client)
    if image:
        if extract_image(image):
            image_metadata = image.attrs
    # now the client can be closed
    close_client(client)
    return image_metadata