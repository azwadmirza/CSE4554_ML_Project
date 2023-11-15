def _init_modules(args, crash_handler):
    """Initialize all 'modules' which need to be initialized.

    Args:
        args: The argparse namespace.
        crash_handler: The CrashHandler instance.
    """
    # pylint: disable=too-many-statements
    log.init.debug("Initializing save manager...")
    save_manager = savemanager.SaveManager(qApp)
    objreg.register('save-manager', save_manager)
    configinit.late_init(save_manager)

    log.init.debug("Checking backend requirements...")
    backendproblem.init()

    log.init.debug("Initializing prompts...")
    prompt.init()

    log.init.debug("Initializing network...")
    networkmanager.init()

    log.init.debug("Initializing proxy...")
    proxy.init()

    log.init.debug("Initializing readline-bridge...")
    readline_bridge = readline.ReadlineBridge()
    objreg.register('readline-bridge', readline_bridge)

    try:
        log.init.debug("Initializing sql...")
        sql.init(os.path.join(standarddir.data(), 'history.sqlite'))

        log.init.debug("Initializing web history...")
        history.init(qApp)
    except sql.SqlError as e:
        if e.environmental:
            error.handle_fatal_exc(e, args, 'Error initializing SQL',
                                   pre_text='Error initializing SQL')
            sys.exit(usertypes.Exit.err_init)
        else:
            raise

    log.init.debug("Initializing completion...")
    completiondelegate.init()

    log.init.debug("Initializing command history...")
    cmdhistory.init()

    log.init.debug("Initializing crashlog...")
    if not args.no_err_windows:
        crash_handler.handle_segfault()

    log.init.debug("Initializing sessions...")
    sessions.init(qApp)

    log.init.debug("Initializing websettings...")
    websettings.init(args)

    log.init.debug("Initializing adblock...")
    host_blocker = adblock.HostBlocker()
    host_blocker.read_hosts()
    objreg.register('host-blocker', host_blocker)

    log.init.debug("Initializing quickmarks...")
    quickmark_manager = urlmarks.QuickmarkManager(qApp)
    objreg.register('quickmark-manager', quickmark_manager)

    log.init.debug("Initializing bookmarks...")
    bookmark_manager = urlmarks.BookmarkManager(qApp)
    objreg.register('bookmark-manager', bookmark_manager)

    log.init.debug("Initializing cookies...")
    cookie_jar = cookies.CookieJar(qApp)
    ram_cookie_jar = cookies.RAMCookieJar(qApp)
    objreg.register('cookie-jar', cookie_jar)
    objreg.register('ram-cookie-jar', ram_cookie_jar)

    log.init.debug("Initializing cache...")
    diskcache = cache.DiskCache(standarddir.cache(), parent=qApp)
    objreg.register('cache', diskcache)

    log.init.debug("Misc initialization...")
    macros.init()
    # Init backend-specific stuff
    browsertab.init()