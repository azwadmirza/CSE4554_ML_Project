def list_cache_nodes_full(opts=None, provider=None, base=None):
    '''
    Return a list of minion data from the cloud cache, rather from the cloud
    providers themselves. This is the cloud cache version of list_nodes_full().
    '''
    if opts is None:
        opts = __opts__
    if opts.get('update_cachedir', False) is False:
        return

    if base is None:
        base = os.path.join(opts['cachedir'], 'active')

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
            for fname in os.listdir(min_dir):
                # Finally, get a list of full minion data
                fpath = os.path.join(min_dir, fname)
                minion_id = fname[:-2]  # strip '.p' from end of msgpack filename
                mode = 'rb' if six.PY3 else 'r'
                with salt.utils.files.fopen(fpath, mode) as fh_:
                    minions[driver][prov][minion_id] = msgpack.load(fh_, encoding='utf-8')
    return minions