def minion_process(queue):
    '''
    Start a minion process
    '''
    import salt.cli.daemons
    # salt_minion spawns this function in a new process

    def suicide_when_without_parent(parent_pid):
        '''
        Have the minion suicide if the parent process is gone

        NOTE: there is a small race issue where the parent PID could be replace
        with another process with the same PID!
        '''
        while True:
            time.sleep(5)
            try:
                # check pid alive (Unix only trick!)
                os.kill(parent_pid, 0)
            except OSError:
                # forcibly exit, regular sys.exit raises an exception-- which
                # isn't sufficient in a thread
                os._exit(999)
    if not salt.utils.is_windows():
        thread = threading.Thread(target=suicide_when_without_parent, args=(os.getppid(),))
        thread.start()

    restart = False
    minion = None
    try:
        minion = salt.cli.daemons.Minion()
        minion.start()
    except (Exception, SaltClientError, SaltReqTimeoutError, SaltSystemExit) as exc:
        log.error(
            'Minion failed to start: {0}'.format(exc.message),
            exc_info=True
        )
        restart = True
    except SystemExit as exc:
        restart = False

    if restart is True:
        log.warn('** Restarting minion **')
        delay = 60
        if minion is not None:
            if hasattr(minion, 'config'):
                delay = minion.config.get('random_reauth_delay', 60)
        random_delay = randint(1, delay)
        log.info('Sleeping random_reauth_delay of {0} seconds'.format(random_delay))
        # preform delay after minion resources have been cleaned
        if minion.options.daemon:
            time.sleep(random_delay)
            salt_minion()
        else:
            queue.put(random_delay)
    else:
        queue.put(0)