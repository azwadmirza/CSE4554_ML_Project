def avail_locations(call=None):
    '''
    List all available locations
    '''
    if call == 'action':
        raise SaltCloudSystemExit(
            'The avail_locations function must be called with '
            '-f or --function, or with the --list-locations option'
        )

    ret = {}
    conn = get_conn(service='SoftLayer_Product_Package')

    locations = conn.getLocations(id=50)
    for location in locations:
        ret[location['id']] = {
            'id': location['id'],
            'name': location['name'],
            'location': location['longName'],
        }

    available = conn.getAvailableLocations(id=50)
    for location in available:
        ret[location['locationId']]['available'] = True

    return ret