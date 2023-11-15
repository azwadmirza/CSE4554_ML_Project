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

    if CONF.get('main', 'single_instance') and not options.new_instance \
      and not running_in_mac_app():
        # Minimal delay (0.1-0.2 secs) to avoid that several
        # instances started at the same time step in their
        # own foots while trying to create the lock file
        time.sleep(random.randrange(1000, 2000, 90)/10000.)

        # Lock file creation
        lock_file = get_conf_path('spyder.lock')
        lock = lockfile.FilesystemLock(lock_file)

        # Try to lock spyder.lock. If it's *possible* to do it, then
        # there is no previous instance running and we can start a
        # new one. If *not*, then there is an instance already
        # running, which is locking that file
        try:
            lock_created = lock.lock()
        except:
            # If locking fails because of errors in the lockfile
            # module, try to remove a possibly stale spyder.lock.
            # This is reported to solve all problems with
            # lockfile (See issue 2363)
            try:
                if os.name == 'nt':
                    if osp.isdir(lock_file):
                        import shutil
                        shutil.rmtree(lock_file, ignore_errors=True)
                else:
                    if osp.islink(lock_file):
                        os.unlink(lock_file)
            except:
                pass

            # Then start Spyder as usual and *don't* continue
            # executing this script because it doesn't make
            # sense
            from spyderlib import spyder
            spyder.main()
            return

        if lock_created:
            # Start a new instance
            if TEST is None:
                atexit.register(lock.unlock)
            from spyderlib import spyder
            spyder.main()
        else:
            # Pass args to Spyder or print an informative
            # message
            if args:
                send_args_to_spyder(args)
            else:
                print("Spyder is already running. If you want to open a new \n"
                      "instance, please pass to it the --new-instance option")
    else:
        from spyderlib import spyder
        spyder.main()