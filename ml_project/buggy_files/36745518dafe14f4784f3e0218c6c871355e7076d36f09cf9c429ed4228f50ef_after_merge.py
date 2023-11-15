def init():
    '''
    Return the list of svn repos
    '''
    bp_ = os.path.join(__opts__['cachedir'], 'svnfs')
    new_remote = False
    repos = []
    svnfs_remotes = salt.utils.repack_dictlist(__opts__['svnfs_remotes'])
    for repo_uri, repo_conf_params in svnfs_remotes.iteritems():

        # Validate and compile per-remote configuration parameters, if present
        repo_conf = dict([(x, None) for x in PER_REMOTE_PARAMS])
        if repo_conf_params is not None:
            repo_conf_params = salt.utils.repack_dictlist(repo_conf_params)
            if not repo_conf_params:
                log.error(
                    'Invalid per-remote configuration for remote {0!r}'
                    .format(repo_uri)
                )
            else:
                for param, value in repo_conf_params.iteritems():
                    if param in PER_REMOTE_PARAMS:
                        repo_conf[param] = value
                    else:
                        log.error(
                            'Invalid configuration parameter {0!r} in remote '
                            '{1!r}. Valid parameters are: {2}. See the '
                            'documentation for further information.'
                            .format(
                                param, repo_uri, ', '.join(PER_REMOTE_PARAMS)
                            )
                        )
        try:
            repo_conf['mountpoint'] = salt.utils.strip_proto(
                repo_conf['mountpoint']
            )
        except TypeError:
            # mountpoint not specified
            pass

        hash_type = getattr(hashlib, __opts__.get('hash_type', 'md5'))
        repo_hash = hash_type(repo_uri).hexdigest()
        rp_ = os.path.join(bp_, repo_hash)
        if not os.path.isdir(rp_):
            os.makedirs(rp_)

        if not os.listdir(rp_):
            # Only attempt a new checkout if the directory is empty.
            try:
                CLIENT.checkout(repo_uri, rp_)
                repos.append(rp_)
                new_remote = True
            except pysvn.ClientError as exc:
                log.error(
                    'Failed to initialize svnfs remote {0!r}: {1}'
                    .format(repo_uri)
                )
                continue
        else:
            # Confirm that there is an svn checkout at the necessary path by
            # running pysvn.Client().status()
            try:
                CLIENT.status(rp_)
            except pysvn.ClientError as exc:
                log.error(
                    'Cache path {0} (corresponding remote: {1}) exists but is '
                    'not a valid subversion checkout. You will need to '
                    'manually delete this directory on the master to continue '
                    'to use this svnfs remote.'.format(rp_, repo_uri)
                )
                continue

        repo_conf.update({
            'repo': rp_,
            'uri': repo_uri,
            'hash': repo_hash,
            'cachedir': rp_
        })
        repos.append(repo_conf)

    if new_remote:
        remote_map = os.path.join(__opts__['cachedir'], 'svnfs/remote_map.txt')
        try:
            with salt.utils.fopen(remote_map, 'w+') as fp_:
                timestamp = datetime.now().strftime('%d %b %Y %H:%M:%S.%f')
                fp_.write('# svnfs_remote map as of {0}\n'.format(timestamp))
                for repo_conf in repos:
                    fp_.write(
                        '{0} = {1}\n'.format(
                            repo_conf['hash'], repo_conf['uri']
                        )
                    )
        except OSError:
            pass
        else:
            log.info('Wrote new svnfs_remote map to {0}'.format(remote_map))

    return repos