def get_location(conn, vm_):
    """
    Return the location object to use
    """
    locations = conn.list_locations()
    vm_location = salt.config.get_cloud_config_value("location", vm_, __opts__)
    for img in locations:
        img_id = str(img.id)
        img_name = str(img.name)

        if vm_location and vm_location in (img_id, img_name):
            return img

    raise SaltCloudNotFound(
        "The specified location, '{}', could not be found.".format(vm_location)
    )