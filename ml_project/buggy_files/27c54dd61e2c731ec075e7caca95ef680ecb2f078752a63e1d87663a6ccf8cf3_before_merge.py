def init():
    '''
    Return the git repo object for this session
    '''
    bp_ = os.path.join(__opts__['cachedir'], 'gitfs')
    provider = _get_provider()
    # ignore git ssl verification if requested
    ssl_verify = 'true' if __opts__.get('gitfs_ssl_verify', True) else 'false'
    new_remote = False
    repos = []

    per_remote_defaults = {}
    for param in PER_REMOTE_PARAMS:
        per_remote_defaults[param] = __opts__['gitfs_{0}'.format(param)]

    for remote in __opts__['gitfs_remotes']:
        repo_conf = copy.deepcopy(per_remote_defaults)
        if isinstance(remote, dict):
            repo_uri = next(iter(remote))
            per_remote_conf = salt.utils.repack_dictlist(remote[repo_uri])
            if not per_remote_conf:
                log.error(
                    'Invalid per-remote configuration for remote {0}. If no '
                    'per-remote parameters are being specified, there may be '
                    'a trailing colon after the URI, which should be removed. '
                    'Check the master configuration file.'.format(repo_uri)
                )
            for param in (x for x in per_remote_conf
                          if x not in PER_REMOTE_PARAMS):
                log.error(
                    'Invalid configuration parameter {0!r} in remote {1}. '
                    'Valid parameters are: {2}. See the documentation for '
                    'further information.'.format(
                        param, repo_uri, ', '.join(PER_REMOTE_PARAMS)
                    )
                )
                per_remote_conf.pop(param)
            repo_conf.update(per_remote_conf)
        else:
            repo_uri = remote

        if not isinstance(repo_uri, string_types):
            log.error(
                'Invalid gitfs remote {0}. Remotes must be strings, you may '
                'need to enclose the URI in quotes'.format(repo_uri)
            )
            continue

        # Check repo_uri against the list of valid protocols
        if provider == 'pygit2':
            transport, _, uri = repo_uri.partition('://')
            if not uri:
                log.error('Invalid gitfs remote {0!r}'.format(repo_uri))
                continue
            elif transport.lower() not in PYGIT2_TRANSPORTS:
                log.error(
                    'Invalid transport {0!r} in gitfs remote {1}. Valid '
                    'transports for pygit2 provider: {2}'
                    .format(transport, repo_uri, ', '.join(PYGIT2_TRANSPORTS))
                )
                continue

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

        try:
            if provider == 'gitpython':
                repo, new = _init_gitpython(rp_, repo_uri, ssl_verify)
                if new:
                    new_remote = True
            elif provider == 'pygit2':
                repo, new = _init_pygit2(rp_, repo_uri, ssl_verify)
                if new:
                    new_remote = True
            elif provider == 'dulwich':
                repo, new = _init_dulwich(rp_, repo_uri, ssl_verify)
                if new:
                    new_remote = True
            else:
                # Should never get here because the provider has been verified
                # in __virtual__(). Log an error and return an empty list.
                log.error(
                    'Unexpected gitfs_provider {0!r}. This is probably a bug.'
                    .format(provider)
                )
                return []

            if repo is not None:
                repo_conf.update({
                    'repo': repo,
                    'uri': repo_uri,
                    'hash': repo_hash,
                    'cachedir': rp_
                })
                repos.append(repo_conf)

        except Exception as exc:
            msg = ('Exception caught while initializing the repo for gitfs: '
                   '{0}.'.format(exc))
            if provider == 'gitpython':
                msg += ' Perhaps git is not available.'
            log.error(msg)
            continue

    if new_remote:
        remote_map = os.path.join(__opts__['cachedir'], 'gitfs/remote_map.txt')
        try:
            with salt.utils.fopen(remote_map, 'w+') as fp_:
                timestamp = datetime.now().strftime('%d %b %Y %H:%M:%S.%f')
                fp_.write('# gitfs_remote map as of {0}\n'.format(timestamp))
                for repo_conf in repos:
                    fp_.write(
                        '{0} = {1}\n'.format(
                            repo_conf['hash'], repo_conf['uri']
                        )
                    )
        except OSError:
            pass
        else:
            log.info('Wrote new gitfs_remote map to {0}'.format(remote_map))

    return repos