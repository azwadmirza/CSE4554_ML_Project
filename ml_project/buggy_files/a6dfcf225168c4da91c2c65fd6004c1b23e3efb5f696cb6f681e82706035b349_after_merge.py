def list_vm_images(image_location=None, publisher_name=None, offer=None, sku=None,
                   all=False):  # pylint: disable=redefined-builtin
    '''vm image list
    :param str image_location:Image location
    :param str publisher_name:Image publisher name, partial name is accepted
    :param str offer:Image offer name, partial name is accepted
    :param str sku:Image sku name, partial name is accepted
    :param bool all:Retrieve image list from live Azure service rather using an offline image list
    '''
    load_thru_services = all

    if load_thru_services:
        if not publisher_name and not offer and not sku:
            logger.warning("You are retrieving all the images from server which could take more than a minute. "
                           "To shorten the wait, provide '--publisher', '--offer' or '--sku'. Partial name search "
                           "is supported.")
        all_images = load_images_thru_services(publisher_name, offer, sku, image_location)
    else:
        logger.warning(
            'You are viewing an offline list of images, use --all to retrieve an up-to-date list')
        all_images = load_images_from_aliases_doc(publisher_name, offer, sku)

    for i in all_images:
        i['urn'] = ':'.join([i['publisher'], i['offer'], i['sku'], i['version']])
    return all_images