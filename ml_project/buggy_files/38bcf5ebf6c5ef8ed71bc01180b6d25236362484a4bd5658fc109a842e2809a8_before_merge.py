def cache_node_list(nodes, provider, opts):
    '''
    If configured to do so, update the cloud cachedir with the current list of
    nodes. Also fires configured events pertaining to the node list.

    .. versionadded:: 2014.7.0
    '''
    if 'update_cachedir' not in opts or not opts['update_cachedir']:
        return

    base = os.path.join(init_cachedir(), 'active')
    driver = next(six.iterkeys(opts['providers'][provider]))
    prov_dir = os.path.join(base, driver, provider)
    if not os.path.exists(prov_dir):
        os.makedirs(prov_dir)

    # Check to see if any nodes in the cache are not in the new list
    missing_node_cache(prov_dir, nodes, provider, opts)

    for node in nodes:
        diff_node_cache(prov_dir, node, nodes[node], opts)
        path = os.path.join(prov_dir, '{0}.p'.format(node))
        with salt.utils.fopen(path, 'w') as fh_:
            msgpack.dump(nodes[node], fh_)