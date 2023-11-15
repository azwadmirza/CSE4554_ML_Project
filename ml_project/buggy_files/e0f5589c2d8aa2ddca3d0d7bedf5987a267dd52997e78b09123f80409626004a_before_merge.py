def diff_node_cache(prov_dir, node, new_data, opts):
    '''
    Check new node data against current cache. If data differ, fire an event
    which consists of the new node data.

    This function will only run if configured to do so in the main Salt Cloud
    configuration file (normally /etc/salt/cloud).

    .. code-block:: yaml

        diff_cache_events: True

    .. versionadded:: 2014.7.0
    '''
    if 'diff_cache_events' not in opts or not opts['diff_cache_events']:
        return

    if node is None:
        return
    path = '{0}.p'.format(os.path.join(prov_dir, node))

    if not os.path.exists(path):
        event_data = _strip_cache_events(new_data, opts)

        fire_event(
            'event',
            'new node found',
            'salt/cloud/{0}/cache_node_new'.format(node),
            args={'new_data': event_data},
            sock_dir=opts.get(
                'sock_dir',
                os.path.join(__opts__['sock_dir'], 'master')),
            transport=opts.get('transport', 'zeromq')
        )
        return

    with salt.utils.fopen(path, 'r') as fh_:
        try:
            cache_data = msgpack.load(fh_)
        except ValueError:
            log.warning('Cache for {0} was corrupt: Deleting'.format(node))
            cache_data = {}

    # Perform a simple diff between the old and the new data, and if it differs,
    # return both dicts.
    # TODO: Return an actual diff
    diff = cmp(new_data, cache_data)
    if diff != 0:
        fire_event(
            'event',
            'node data differs',
            'salt/cloud/{0}/cache_node_diff'.format(node),
            args={
                'new_data': _strip_cache_events(new_data, opts),
                'cache_data': _strip_cache_events(cache_data, opts),
            },
            sock_dir=opts.get(
                'sock_dir',
                os.path.join(__opts__['sock_dir'], 'master')),
            transport=opts.get('transport', 'zeromq')
        )