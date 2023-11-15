def update():
    '''
    Execute a git fetch on all of the repos
    '''
    # data for the fileserver event
    data = {'changed': False,
            'backend': 'gitfs'}
    provider = _get_provider()
    # _clear_old_remotes runs init(), so use the value from there to avoid a
    # second init()
    data['changed'], repos = _clear_old_remotes()
    for repo in repos:
        if os.path.exists(repo['lockfile']):
            log.warning(
                'Update lockfile is present for gitfs remote {0}, skipping. '
                'If this warning persists, it is possible that the update '
                'process was interrupted. Removing {1} or running '
                '\'salt-run fileserver.clear_lock gitfs\' will allow updates '
                'to continue for this remote.'
                .format(repo['url'], repo['lockfile'])
            )
            continue
        _, errors = lock(repo)
        if errors:
            log.error('Unable to set update lock for gitfs remote {0}, '
                      'skipping.'.format(repo['url']))
            continue
        log.debug('gitfs is fetching from {0}'.format(repo['url']))
        try:
            if provider == 'gitpython':
                origin = repo['repo'].remotes[0]
                try:
                    fetch_results = origin.fetch()
                except AssertionError:
                    fetch_results = origin.fetch()
                cleaned = _clean_stale(repo)
                if fetch_results or cleaned:
                    data['changed'] = True
            elif provider == 'pygit2':
                origin = repo['repo'].remotes[0]
                refs_pre = repo['repo'].listall_references()
                try:
                    origin.credentials = repo['credentials']
                except KeyError:
                    # No credentials configured for this repo
                    pass
                try:
                    fetch = origin.fetch()
                except pygit2.errors.GitError as exc:
                    # Using exc.__str__() here to avoid deprecation warning
                    # when referencing exc.message
                    if 'unsupported url protocol' in exc.__str__().lower() \
                            and isinstance(repo.get('credentials'),
                                           pygit2.Keypair):
                        log.error(
                            'Unable to fetch SSH-based gitfs remote {0}. '
                            'libgit2 must be compiled with libssh2 to support '
                            'SSH authentication.'.format(repo['url'])
                        )
                        continue
                    raise
                try:
                    # pygit2.Remote.fetch() returns a dict in pygit2 < 0.21.0
                    received_objects = fetch['received_objects']
                except (AttributeError, TypeError):
                    # pygit2.Remote.fetch() returns a class instance in
                    # pygit2 >= 0.21.0
                    received_objects = fetch.received_objects
                if received_objects != 0:
                    log.debug(
                        'gitfs received {0} objects for remote {1}'
                        .format(received_objects, repo['url'])
                    )
                else:
                    log.debug(
                        'gitfs remote {0} is up-to-date'
                        .format(repo['url'])
                    )
                # Clean up any stale refs
                refs_post = repo['repo'].listall_references()
                cleaned = _clean_stale(repo, refs_post)
                if received_objects or refs_pre != refs_post or cleaned:
                    data['changed'] = True
            elif provider == 'dulwich':
                # origin is just a url here, there is no origin object
                origin = repo['url']
                client, path = \
                    dulwich.client.get_transport_and_path_from_url(
                        origin, thin_packs=True
                    )
                refs_pre = repo['repo'].get_refs()
                try:
                    refs_post = client.fetch(path, repo['repo'])
                except dulwich.errors.NotGitRepository:
                    log.error(
                        'Dulwich does not recognize remote {0} as a valid '
                        'remote URL. Perhaps it is missing \'.git\' at the '
                        'end.'.format(repo['url'])
                    )
                    continue
                except KeyError:
                    log.error(
                        'Local repository cachedir {0!r} (corresponding '
                        'remote: {1}) has been corrupted. Salt will now '
                        'attempt to remove the local checkout to allow it to '
                        'be re-initialized in the next fileserver cache '
                        'update.'
                        .format(repo['cachedir'], repo['url'])
                    )
                    try:
                        salt.utils.rm_rf(repo['cachedir'])
                    except OSError as exc:
                        log.error(
                            'Unable to remove {0!r}: {1}'
                            .format(repo['cachedir'], exc)
                        )
                    continue
                if refs_post is None:
                    # Empty repository
                    log.warning(
                        'gitfs remote {0!r} is an empty repository and will '
                        'be skipped.'.format(origin)
                    )
                    continue
                if refs_pre != refs_post:
                    data['changed'] = True
                    # Update local refs
                    for ref in _dulwich_env_refs(refs_post):
                        repo['repo'][ref] = refs_post[ref]
                    # Prune stale refs
                    for ref in repo['repo'].get_refs():
                        if ref not in refs_post:
                            del repo['repo'][ref]
        except Exception as exc:
            # Do not use {0!r} in the error message, as exc is not a string
            log.error(
                'Exception \'{0}\' caught while fetching gitfs remote {1}'
                .format(exc, repo['url']),
                exc_info_on_loglevel=logging.DEBUG
            )
        finally:
            clear_lock(repo)

    env_cache = os.path.join(__opts__['cachedir'], 'gitfs/envs.p')
    if data.get('changed', False) is True or not os.path.isfile(env_cache):
        env_cachedir = os.path.dirname(env_cache)
        if not os.path.exists(env_cachedir):
            os.makedirs(env_cachedir)
        new_envs = envs(ignore_cache=True)
        serial = salt.payload.Serial(__opts__)
        with salt.utils.fopen(env_cache, 'w+') as fp_:
            fp_.write(serial.dumps(new_envs))
            log.trace('Wrote env cache data to {0}'.format(env_cache))

    # if there is a change, fire an event
    if __opts__.get('fileserver_events', False):
        event = salt.utils.event.get_event(
                'master',
                __opts__['sock_dir'],
                __opts__['transport'],
                opts=__opts__,
                listen=False)
        event.fire_event(data, tagify(['gitfs', 'update'], prefix='fileserver'))
    try:
        salt.fileserver.reap_fileserver_cache_dir(
            os.path.join(__opts__['cachedir'], 'gitfs/hash'),
            find_file
        )
    except (IOError, OSError):
        # Hash file won't exist if no files have yet been served up
        pass