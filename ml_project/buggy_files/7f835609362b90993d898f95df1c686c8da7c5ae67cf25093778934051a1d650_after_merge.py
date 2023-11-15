def get_image(conn, vm_):
    """
    Return the image object to use
    """
    images = conn.list_images()
    vm_image = salt.config.get_cloud_config_value("image", vm_, __opts__)

    for img in images:
        img_id = str(img.id)
        img_name = str(img.name)

        if vm_image and vm_image in (img_id, img_name):
            return img

    raise SaltCloudNotFound(
        "The specified image, '{}', could not be found.".format(vm_image)
    )