def extract_image(args):
    """The image can either be downloaded from a container registry or provided
    as an image tarball. Extract the image into a working directory accordingly
    Return an image name and tag and an image digest if it exists"""
    if args.docker_image:
        # extract the docker image
        image_attrs = docker_api.dump_docker_image(args.docker_image)
        if image_attrs:
            # repo name and digest is preferred, but if that doesn't exist
            # the repo name and tag will do. If neither exist use repo Id.
            if image_attrs['Id']:
                image_string = image_attrs['Id']
            if image_attrs['RepoTags']:
                image_string = image_attrs['RepoTags'][0]
            if image_attrs['RepoDigests']:
                image_string = image_attrs['RepoDigests'][0]
            return image_string
        logger.critical("Cannot extract Docker image")
    if args.raw_image:
        # for now we assume that the raw image tarball is always
        # the product of "docker save", hence it will be in
        # the docker style layout
        if rootfs.extract_tarfile(args.raw_image, rootfs.get_working_dir()):
            return args.raw_image
        logger.critical("Cannot extract raw image")
    return None