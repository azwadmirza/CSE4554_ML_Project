def extract_image(args):
    """The image can either be downloaded from a container registry or provided
    as an image tarball. Extract the image into a working directory accordingly
    Return an image name and tag and an image digest if it exists"""
    if args.docker_image:
        # extract the docker image
        image_attrs = docker_api.dump_docker_image(args.docker_image)
        if image_attrs:
            if image_attrs['RepoTags']:
                image_string = image_attrs['RepoTags'][0]
            if image_attrs['RepoDigests']:
                image_digest = image_attrs['RepoDigests'][0]
            return image_string, image_digest
        logger.critical("Cannot extract Docker image")
    if args.raw_image:
        # for now we assume that the raw image tarball is always
        # the product of "docker save", hence it will be in
        # the docker style layout
        if rootfs.extract_tarfile(args.raw_image, rootfs.get_working_dir()):
            return args.raw_image, None
        logger.critical("Cannot extract raw image")
    return None, None