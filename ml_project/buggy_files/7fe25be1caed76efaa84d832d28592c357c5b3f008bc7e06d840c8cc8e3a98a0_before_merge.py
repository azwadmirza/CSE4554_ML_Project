def cachedir_index_add(minion_id, profile, driver, provider, base=None):
    '''
    Add an entry to the cachedir index. This generally only needs to happen when
    a new instance is created. This entry should contain:

    .. code-block:: yaml

        - minion_id
        - profile used to create the instance
        - provider and driver name

    The intent of this function is to speed up lookups for the cloud roster for
    salt-ssh. However, other code that makes use of profile information can also
    make use of this function.
    '''
    base = init_cachedir(base)
    index_file = os.path.join(base, 'index.p')
    lock_file(index_file)

    if os.path.exists(index_file):
        with salt.utils.fopen(index_file, 'r') as fh_:
            index = msgpack.load(fh_)
    else:
        index = {}

    prov_comps = provider.split(':')

    index.update({
        minion_id: {
            'id': minion_id,
            'profile': profile,
            'driver': driver,
            'provider': prov_comps[0],
        }
    })

    with salt.utils.fopen(index_file, 'w') as fh_:
        msgpack.dump(index, fh_)

    unlock_file(index_file)