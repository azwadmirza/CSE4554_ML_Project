def salt_minion():
    '''
    Start the salt minion.
    '''
    import salt.cli.daemons
    import multiprocessing
    if '' in sys.path:
        sys.path.remove('')

    if salt.utils.is_windows():
        minion = salt.cli.daemons.Minion()
        minion.start()
        return

    if '--disable-keepalive' in sys.argv:
        sys.argv.remove('--disable-keepalive')
        minion = salt.cli.daemons.Minion()
        minion.start()
        return

    # keep one minion subprocess running
    while True:
        try:
            queue = multiprocessing.Queue()
        except Exception:
            # This breaks in containers
            minion = salt.cli.daemons.Minion()
            minion.start()
            return
        process = multiprocessing.Process(target=minion_process, args=(queue,))
        process.start()
        try:
            process.join()
            try:
                restart_delay = queue.get(block=False)
            except Exception:
                if process.exitcode == 0:
                    # Minion process ended naturally, Ctrl+C or --version
                    break
                restart_delay = 60
            if restart_delay == 0:
                # Minion process ended naturally, Ctrl+C, --version, etc.
                break
            # delay restart to reduce flooding and allow network resources to close
            time.sleep(restart_delay)
        except KeyboardInterrupt:
            break
        # need to reset logging because new minion objects
        # cause extra log handlers to accumulate
        rlogger = logging.getLogger()
        for handler in rlogger.handlers:
            rlogger.removeHandler(handler)
        logging.basicConfig()