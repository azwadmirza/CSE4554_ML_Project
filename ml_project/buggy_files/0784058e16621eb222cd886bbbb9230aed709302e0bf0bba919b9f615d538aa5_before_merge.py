def update():
    '''
    Execute a git pull on all of the repos
    '''
    # data for the fileserver event
    data = {'changed': False,
            'backend': 'gitfs'}
    pid = os.getpid()
    repos = init()
    for repo in repos:
        origin = repo.remotes[0]
        lk_fn = os.path.join(repo.working_dir, 'update.lk')
        with salt.utils.fopen(lk_fn, 'w+') as fp_:
            fp_.write(str(pid))
        try:
            for fetch in origin.fetch():
                if fetch.old_commit is not None:
                    data['changed'] = True
        except Exception as exc:
            log.warning('GitPython exception caught while fetching: '
                        '{0}'.format(exc))
        try:
            os.remove(lk_fn)
        except (IOError, OSError):
            pass

    # if there is a change, fire an event
    event = salt.utils.event.MasterEvent(__opts__['sock_dir'])
    event.fire_event(data, tagify(['gitfs', 'update'], prefix='fileserver'))
    try:
        salt.fileserver.reap_fileserver_cache_dir(
            os.path.join(__opts__['cachedir'], 'gitfs/hash'),
            find_file
        )
    except (IOError, OSError):
        # Hash file won't exist if no files have yet been served up
        pass