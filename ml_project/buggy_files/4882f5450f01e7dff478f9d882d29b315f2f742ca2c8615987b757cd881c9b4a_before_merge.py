  def demote_bootstrap(cls):
    TRACER.log('Bootstrap complete, performing final sys.path modifications...')

    bootstrap_path = __file__
    module_import_path = __name__.split('.')

    # For example, our __file__ might be requests.pex/.bootstrap/pex/pex.pyc and our import path
    # pex.pex; so we walk back through all the module components of our import path to find the
    # base sys.path entry where we were found (requests.pex/.bootstrap in this example).
    for _ in module_import_path:
      bootstrap_path = os.path.dirname(bootstrap_path)
    bootstrap_path_index = sys.path.index(bootstrap_path)

    should_log = {level: TRACER.should_log(V=level) for level in range(1, 10)}

    def log(msg, V=1):
      if should_log.get(V, False):
        print('pex: {}'.format(msg), file=sys.stderr)

    # Move the third party resources pex uses to the end of sys.path for the duration of the run to
    # allow conflicting versions supplied by user dependencies to win during the course of the
    # execution of user code.
    unregister_finders()
    third_party.uninstall()
    for _, mod, _ in pkgutil.iter_modules([bootstrap_path]):
      if mod in sys.modules:
        log('Un-importing bootstrap dependency %s from %s' % (mod, bootstrap_path), V=2)
        sys.modules.pop(mod)
        log('un-imported {}'.format(mod), V=9)

        submod_prefix = mod + '.'
        for submod in sorted(m for m in sys.modules.keys() if m.startswith(submod_prefix)):
          sys.modules.pop(submod)
          log('un-imported {}'.format(submod), V=9)

    sys.path.pop(bootstrap_path_index)
    sys.path.append(bootstrap_path)

    import pex
    log('Re-imported pex from {}'.format(pex.__path__), V=3)

    log('PYTHONPATH contains:')
    for element in sys.path:
      log('  %c %s' % (' ' if os.path.exists(element) else '*', element))
    log('  * - paths that do not exist or will be imported via zipimport')