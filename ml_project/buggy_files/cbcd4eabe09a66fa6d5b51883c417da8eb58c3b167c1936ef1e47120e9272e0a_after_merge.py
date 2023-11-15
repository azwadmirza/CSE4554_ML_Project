def main(args=None):
    colorful = False
    if sys.stderr.isatty() and os.name != 'nt':
        colorful = True

    ColorfulStderrHandler._colorful = colorful

    if args is None:
        args = sys.argv[1:]
    quiet = False
    if len(args) > 0 and args[0] == b'build' and b'--strict' in args:
        LOGGER.notice('Running in strict mode')
        STRICT_HANDLER.push_application()
    if len(args) > 0 and args[0] == b'build' and b'-q' in args or b'--quiet' in args:
        nullhandler = NullHandler()
        nullhandler.push_application()
        quiet = True
    global config

    # Those commands do not require a `conf.py`.  (Issue #1132)
    # Moreover, actually having one somewhere in the tree can be bad, putting
    # the output of that command (the new site) in an unknown directory that is
    # not the current working directory.  (does not apply to `version`)
    argname = args[0] if len(args) > 0 else None
    # FIXME there are import plugins in the repo, so how do we handle this?
    if argname and argname not in ['init', 'version'] and not argname.startswith('import_'):
        root = get_root_dir()
        if root:
            os.chdir(root)

    sys.path.append('')
    try:
        import conf
        _reload(conf)
        config = conf.__dict__
    except Exception:
        if os.path.exists('conf.py'):
            msg = traceback.format_exc(0).splitlines()[1]
            LOGGER.error('In conf.py line {0}: {1}'.format(sys.exc_info()[2].tb_lineno, msg))
            sys.exit(1)
        config = {}

    invariant = False

    if len(args) > 0 and args[0] == b'build' and b'--invariant' in args:
        try:
            import freezegun
            freeze = freezegun.freeze_time("2014-01-01")
            freeze.start()
            invariant = True
        except ImportError:
            req_missing(['freezegun'], 'perform invariant builds')

    if config:
        if os.path.exists('plugins') and not os.path.exists('plugins/__init__.py'):
            with open('plugins/__init__.py', 'w') as fh:
                fh.write('# Plugin modules go here.')

    config['__colorful__'] = colorful
    config['__invariant__'] = invariant
    config['__quiet__'] = quiet

    site = Nikola(**config)
    _ = DoitNikola(site, quiet).run(args)

    if site.invariant:
        freeze.stop()
    return _