def cache_node(node, provider, opts):
    '''
    Cache node individually

    .. versionadded:: 2014.7.0
    '''
    if isinstance(opts, dict):
        __opts__.update(opts)

    if 'update_cachedir' not in __opts__ or not __opts__['update_cachedir']:
        return

    if not os.path.exists(os.path.join(__opts__['cachedir'], 'active')):
        init_cachedir()

    base = os.path.join(__opts__['cachedir'], 'active')
    provider, driver = provider.split(':')
    prov_dir = os.path.join(base, driver, provider)
    if not os.path.exists(prov_dir):
        os.makedirs(prov_dir)
    path = os.path.join(prov_dir, '{0}.p'.format(node['name']))
    mode = 'wb' if six.PY3 else 'w'
    with salt.utils.files.fopen(path, mode) as fh_:
        msgpack.dump(node, fh_)