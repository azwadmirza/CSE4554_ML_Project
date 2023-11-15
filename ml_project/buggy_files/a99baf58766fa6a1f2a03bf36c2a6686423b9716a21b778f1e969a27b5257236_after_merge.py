def versions():
    '''
    Check the version of active minions

    CLI Example:

    .. code-block:: bash

        salt-run manage.versions
    '''
    ret = {}
    client = salt.client.get_local_client(__opts__['conf_file'])
    try:
        minions = client.cmd('*', 'test.version', timeout=__opts__['timeout'])
    except SaltClientError as client_error:
        print(client_error)
        return ret

    labels = {
        -2: 'Minion offline',
        -1: 'Minion requires update',
        0: 'Up to date',
        1: 'Minion newer than master',
        2: 'Master',
    }

    version_status = {}

    master_version = salt.version.__saltstack_version__

    for minion in minions:
        if not minions[minion]:
            minion_version = False
            ver_diff = -2
        else:
            minion_version = salt.version.SaltStackVersion.parse(minions[minion])
            ver_diff = cmp(minion_version, master_version)

        if ver_diff not in version_status:
            version_status[ver_diff] = {}
        if minion_version:
            version_status[ver_diff][minion] = minion_version.string
        else:
            version_status[ver_diff][minion] = minion_version

    # Add version of Master to output
    version_status[2] = master_version.string

    for key in version_status:
        if key == 2:
            ret[labels[key]] = version_status[2]
        else:
            for minion in sorted(version_status[key]):
                ret.setdefault(labels[key], {})[minion] = version_status[key][minion]
    return ret