def docker_to_uuid(uuid):
    '''
    Get the image uuid from an imported docker image

    .. versionadded:: 2019.2.0
    '''
    if _is_uuid(uuid):
        return uuid
    if _is_docker_uuid(uuid):
        images = list_installed(verbose=True)
        for image_uuid in images:
            if 'name' not in images[image_uuid]:
                continue
            if images[image_uuid]['name'] == uuid:
                return image_uuid
    return None