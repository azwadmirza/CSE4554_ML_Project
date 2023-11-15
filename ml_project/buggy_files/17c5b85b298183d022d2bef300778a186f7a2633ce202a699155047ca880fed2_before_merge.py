def main():
    """
    Start Spyder application.

    If single instance mode is turned on (default behavior) and an instance of
    Spyder is already running, this will just parse and send command line
    options to the application.
    """
    # Renaming old configuration files (the '.' prefix has been removed)
    # (except for .spyder.ini --> spyder.ini, which is done in userconfig.py)
    if DEV is None:
        cpath = get_conf_path()
        for fname in os.listdir(cpath):
            if fname.startswith('.'):
                old, new = osp.join(cpath, fname), osp.join(cpath, fname[1:])
                try:
                    os.rename(old, new)
                except OSError:
                    pass

    # Parse command line options
    options, args = get_options()

    # Store variable to be used in self.restart (restart spyder instance)
    os.environ['SPYDER_ARGS'] = str(sys.argv[1:])

    if CONF.get('main', 'single_instance') and not options.new_instance \
      and not running_in_mac_app():
        # Minimal delay (0.1-0.2 secs) to avoid that several
        # instances started at the same time step in their
        # own foots while trying to create the lock file
        time.sleep(random.randrange(1000, 2000, 90)/10000.)
        
        # Lock file creation
        lockf = get_conf_path('spyder.lock')
        lock = lockfile.FilesystemLock(lockf)
        
        # lock.lock() tries to lock spyder.lock. If it fails,
        # it returns False and so we try to start the client
        if not lock.lock():
            if args:
                send_args_to_spyder(args)
            else:
                print("Spyder is already running. If you want to open a new \n"
                      "instance, please pass to it the --new-instance option")
        else:
            if TEST is None:
                atexit.register(lock.unlock)
            from spyderlib import spyder
            spyder.main()
    else:
        from spyderlib import spyder
        spyder.main()