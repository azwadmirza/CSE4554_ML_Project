def list_cache_nodes_full(opts, provider=None, base=None):
    '''
    Return a list of minion data from the cloud cache, rather from the cloud
    providers themselves. This is the cloud cache version of list_nodes_full().
    '''
    if opts.get('update_cachedir', False) is False:
        return

    if base is None:
        base = os.path.join(__opts__['cachedir'], 'active')

    minions = {}
    # First, get a list of all drivers in use
    for driver in os.listdir(base):
        minions[driver] = {}
        prov_dir = os.path.join(base, driver)
        # Then, get a list of all providers per driver
        for prov in os.listdir(prov_dir):
            # If a specific provider is requested, filter out everyone else
            if provider and provider != prov:
                continue
            minions[driver][prov] = {}
            min_dir = os.path.join(prov_dir, prov)
            # Get a list of all nodes per provider
            for minion_id in os.listdir(min_dir):
                # Finally, get a list of full minion data
                fname = '{0}.p'.format(minion_id)
                fpath = os.path.join(min_dir, fname)
                with salt.utils.fopen(fpath, 'r') as fh_:
                    minions[driver][prov][minion_id] = msgpack.load(fh_, encoding=MSGPACK_ENCODING)

    return minions