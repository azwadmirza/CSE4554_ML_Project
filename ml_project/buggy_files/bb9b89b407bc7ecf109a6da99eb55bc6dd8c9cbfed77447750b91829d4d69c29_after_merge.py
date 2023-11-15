def get_location(opts=None, provider=None):
    '''
    Return the region to use, in this order:
        opts['location']
        provider['location']
        get_region_from_metadata()
        DEFAULT_LOCATION
    '''
    if opts is None:
        opts = {}
    ret = opts.get('location')
    if ret is None and provider is not None:
        ret = provider.get('location')
    if ret is None:
        ret = get_region_from_metadata()
    if ret is None:
        ret = DEFAULT_LOCATION
    return ret