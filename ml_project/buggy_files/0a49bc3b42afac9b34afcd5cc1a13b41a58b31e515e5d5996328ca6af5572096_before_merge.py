def init():
    '''
    Return a list of hglib objects for the various hgfs remotes
    '''
    bp_ = os.path.join(__opts__['cachedir'], 'hgfs')
    new_remote = False
    repos = []
    hgfs_remotes = salt.utils.repack_dictlist(__opts__['hgfs_remotes'])
    for repo_uri, repo_conf_params in hgfs_remotes.iteritems():

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

        repo_hash = hashlib.md5(repo_uri).hexdigest()
        rp_ = os.path.join(bp_, repo_hash)
        if not os.path.isdir(rp_):
            os.makedirs(rp_)

        if not os.listdir(rp_):
            # Only init if the directory is empty.
            hglib.init(rp_)
            new_remote = True
        try:
            repo = hglib.open(rp_)
        except hglib.error.ServerError:
            log.error(
                'Cache path {0} (corresponding remote: {1}) exists but is not '
                'a valid mercurial repository. You will need to manually '
                'delete this directory on the master to continue to use this '
                'hgfs remote.'.format(rp_, repo_uri)
            )
            continue

        refs = repo.config(names='paths')
        if not refs:
            # Write an hgrc defining the remote URI
            hgconfpath = os.path.join(rp_, '.hg', 'hgrc')
            with salt.utils.fopen(hgconfpath, 'w+') as hgconfig:
                hgconfig.write('[paths]\n')
                hgconfig.write('default = {0}\n'.format(repo_uri))

        repo_conf.update({
            'repo': repo,
            'uri': repo_uri,
            'hash': repo_hash,
            'cachedir': rp_
        })
        repos.append(repo_conf)
        repo.close()

    if new_remote:
        remote_map = os.path.join(__opts__['cachedir'], 'hgfs/remote_map.txt')
        try:
            with salt.utils.fopen(remote_map, 'w+') as fp_:
                timestamp = datetime.now().strftime('%d %b %Y %H:%M:%S.%f')
                fp_.write('# hgfs_remote map as of {0}\n'.format(timestamp))
                for repo_conf in repos:
                    fp_.write(
                        '{0} = {1}\n'.format(
                            repo_conf['hash'], repo_conf['uri']
                        )
                    )
        except OSError:
            pass
        else:
            log.info('Wrote new hgfs_remote map to {0}'.format(remote_map))

    return repos