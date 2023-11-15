def get_node_syncer(local_dir, remote_dir=None, sync_function=None):
    """Returns a NodeSyncer.

    Args:
        local_dir (str): Source directory for syncing.
        remote_dir (str): Target directory for syncing. If not provided, a
            noop Syncer is returned.
        sync_function (func|str|bool): Function for syncing the local_dir to
            remote_dir. If string, then it must be a string template for
            syncer to run. If True or not provided, it defaults rsync. If
            False, a noop Syncer is returned.
    """
    key = (local_dir, remote_dir)
    if key in _syncers:
        return _syncers[key]
    elif not remote_dir or sync_function is False:
        sync_client = NOOP
    elif sync_function and sync_function is not True:
        sync_client = get_sync_client(sync_function)
    else:
        sync = log_sync_template()
        if sync:
            sync_client = CommandBasedClient(sync, sync)
            sync_client.set_logdir(local_dir)
        else:
            sync_client = NOOP

    _syncers[key] = NodeSyncer(local_dir, remote_dir, sync_client)
    return _syncers[key]