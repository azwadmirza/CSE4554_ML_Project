def avail_images(conn=None, call=None):
    '''
    Return a dict of all available VM images on the cloud provider with
    relevant data
    '''
    if call == 'action':
        raise SaltCloudSystemExit(
            'The avail_images function must be called with '
            '-f or --function, or with the --list-images option'
        )

    if not conn:
        conn = get_conn()   # pylint: disable=E0602

    images = conn.list_images()
    ret = {}
    for img in images:
        if isinstance(img.name, string_types) and not six.PY3:
            img_name = img.name.encode('ascii', 'salt-cloud-force-ascii')
        else:
            img_name = str(img.name)

        ret[img_name] = {}
        for attr in dir(img):
            if attr.startswith('_'):
                continue
            attr_value = getattr(img, attr)
            if isinstance(attr_value, string_types) and not six.PY3:
                attr_value = attr_value.encode(
                    'ascii', 'salt-cloud-force-ascii'
                )
            ret[img_name][attr] = attr_value
    return ret