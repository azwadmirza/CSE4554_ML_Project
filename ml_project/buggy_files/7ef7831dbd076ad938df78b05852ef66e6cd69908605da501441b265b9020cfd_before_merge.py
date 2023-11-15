def create_node(**kwargs):
    '''
    convenience function to make the rest api call for node creation.
    '''
    name = kwargs['name']
    size = kwargs['size']
    image = kwargs['image']
    location = kwargs['location']
    networks = kwargs['networks']

    data = json.dumps({
        'name': name,
        'package': size['name'],
        'image': image['name'],
        'networks': networks
    })

    try:
        ret = query(command='/my/machines', data=data, method='POST',
                     location=location)
        if ret[0] in VALID_RESPONSE_CODES:
            return ret[1]
    except Exception as exc:
        log.error(
            'Failed to create node {0}: {1}'.format(name, exc)
        )

    return {}