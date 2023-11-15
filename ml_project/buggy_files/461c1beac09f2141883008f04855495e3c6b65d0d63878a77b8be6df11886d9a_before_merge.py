def main(args=None):
    """Run Nikola."""
    colorful = False
    if sys.stderr.isatty() and os.name != 'nt' and os.getenv('NIKOLA_MONO') is None and os.getenv('TERM') != 'dumb':
        colorful = True

    ColorfulStderrHandler._colorful = colorful

    if args is None:
        args = sys.argv[1:]

    oargs = args
    args = [sys_decode(arg) for arg in args]

    conf_filename = 'conf.py'
    conf_filename_changed = False
    for index, arg in enumerate(args):
        if arg[:7] == '--conf=':
            del args[index]
            del oargs[index]
            conf_filename = arg[7:]
            conf_filename_changed = True
            break

    quiet = False
    strict = False
    if len(args) > 0 and args[0] == 'build' and '--strict' in args:
        LOGGER.notice('Running in strict mode')
        STRICT_HANDLER.push_application()
        strict = True
    if len(args) > 0 and args[0] == 'build' and '-q' in args or '--quiet' in args:
        NullHandler().push_application()
        quiet = True
    if not quiet and not strict:
        NullHandler().push_application()
        STDERR_HANDLER[0].push_application()

    global config

    original_cwd = os.getcwd()

    # Those commands do not require a `conf.py`.  (Issue #1132)
    # Moreover, actually having one somewhere in the tree can be bad, putting
    # the output of that command (the new site) in an unknown directory that is
    # not the current working directory.  (does not apply to `version`)
    argname = args[0] if len(args) > 0 else None
    if argname and argname not in ['init', 'version'] and not argname.startswith('import_'):
        root = get_root_dir()
        if root:
            os.chdir(root)
        # Help and imports don't require config, but can use one if it exists
        needs_config_file = (argname != 'help') and not argname.startswith('import_')
        LOGGER.debug("Website root: {0!r}", root)
    else:
        needs_config_file = False

    old_path = sys.path

    try:
        sys.path = sys.path[:]
        sys.path.insert(0, os.path.dirname(conf_filename))
        with open(conf_filename, "rb") as file:
            config = imp.load_module(conf_filename, file, conf_filename, (None, "rb", imp.PY_SOURCE)).__dict__
    except Exception:
        config = {}
        if os.path.exists(conf_filename):
            msg = traceback.format_exc()
            LOGGER.error('"{0}" cannot be parsed.\n{1}'.format(conf_filename, msg))
            return 1
        elif needs_config_file and conf_filename_changed:
            LOGGER.error('Cannot find configuration file "{0}".'.format(conf_filename))
            return 1
    finally:
        sys.path = old_path

    if conf_filename_changed:
        LOGGER.info("Using config file '{0}'".format(conf_filename))

    invariant = False

    if len(args) > 0 and args[0] == 'build' and '--invariant' in args:
        try:
            import freezegun
            freeze = freezegun.freeze_time("2038-01-01")
            freeze.start()
            invariant = True
        except ImportError:
            req_missing(['freezegun'], 'perform invariant builds')

    if config:
        if os.path.isdir('plugins') and not os.path.exists('plugins/__init__.py'):
            with open('plugins/__init__.py', 'w') as fh:
                fh.write('# Plugin modules go here.')

    config['__colorful__'] = colorful
    config['__invariant__'] = invariant
    config['__quiet__'] = quiet
    config['__configuration_filename__'] = conf_filename
    config['__cwd__'] = original_cwd
    site = Nikola(**config)
    DN = DoitNikola(site, quiet)
    if _RETURN_DOITNIKOLA:
        return DN
    _ = DN.run(oargs)

    if site.invariant:
        freeze.stop()
    return _