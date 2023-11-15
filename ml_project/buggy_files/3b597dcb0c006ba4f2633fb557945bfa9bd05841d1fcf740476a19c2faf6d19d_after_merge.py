def push(path, keep_symlinks=False, upload_path=None):
    '''
    Push a file from the minion up to the master, the file will be saved to
    the salt master in the master's minion files cachedir
    (defaults to ``/var/cache/salt/master/minions/minion-id/files``)

    Since this feature allows a minion to push a file up to the master server
    it is disabled by default for security purposes. To enable, set
    ``file_recv`` to ``True`` in the master configuration file, and restart the
    master.

    keep_symlinks
        Keep the path value without resolving its canonical form

    upload_path
        Provide a different path inside the master's minion files cachedir

    CLI Example:

    .. code-block:: bash

        salt '*' cp.push /etc/fstab
        salt '*' cp.push /etc/system-release keep_symlinks=True
        salt '*' cp.push /etc/fstab upload_path='/new/path/fstab'
    '''
    log.debug('Trying to copy {0!r} to master'.format(path))
    if '../' in path or not os.path.isabs(path):
        log.debug('Path must be absolute, returning False')
        return False
    if not keep_symlinks:
        path = os.path.realpath(path)
    if not os.path.isfile(path):
        log.debug('Path failed os.path.isfile check, returning False')
        return False
    auth = _auth()

    if upload_path:
        if '../' in upload_path:
            log.debug('Path must be absolute, returning False')
            log.debug('Bad path: {0}'.format(upload_path))
            return False
        load_path = upload_path.lstrip(os.sep)
    else:
        load_path = path.lstrip(os.sep)
    # Normalize the path. This does not eliminate
    # the possibility that relative entries will still be present
    load_path_normal = os.path.normpath(load_path)

    # If this is Windows and a drive letter is present, remove it
    load_path_split_drive = os.path.splitdrive(load_path_normal)[1]

    # Finally, split the remaining path into a list for delivery to the master
    load_path_list = os.path.split(load_path_split_drive)

    load = {'cmd': '_file_recv',
            'id': __opts__['id'],
            'path': load_path_list,
            'tok': auth.gen_token('salt')}
    channel = salt.transport.Channel.factory(__opts__)
    with salt.utils.fopen(path, 'rb') as fp_:
        init_send = False
        while True:
            load['loc'] = fp_.tell()
            load['data'] = fp_.read(__opts__['file_buffer_size'])
            if not load['data'] and init_send:
                return True
            ret = channel.send(load)
            if not ret:
                log.error('cp.push Failed transfer failed. Ensure master has '
                '\'file_recv\' set to \'True\' and that the file is not '
                'larger than the \'file_recv_size_max\' setting on the master.')
                return ret
            init_send = True