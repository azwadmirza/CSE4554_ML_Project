  def demote_bootstrap(cls):
    TRACER.log('Bootstrap complete, performing final sys.path modifications...')

    bootstrap_path = __file__
    module_import_path = __name__.split('.')
    root_package = module_import_path[0]

    # For example, our __file__ might be requests.pex/.bootstrap/_pex/pex.pyc and our import path
    # _pex.pex; so we walk back through all the module components of our import path to find the
    # base sys.path entry where we were found (requests.pex/.bootstrap in this example).
    for _ in module_import_path:
      bootstrap_path = os.path.dirname(bootstrap_path)
    bootstrap_path_index = sys.path.index(bootstrap_path)

    # Move the third party resources pex uses to the end of sys.path for the duration of the run to
    # allow conflicting versions supplied by user dependencies to win during the course of the
    # execution of user code.
    for _, mod, _ in pkgutil.iter_modules([bootstrap_path]):
      if mod != root_package:  # We let _pex stay imported
        TRACER.log('Un-importing third party bootstrap dependency %s from %s'
                   % (mod, bootstrap_path))
        sys.modules.pop(mod)
    sys.path.pop(bootstrap_path_index)
    sys.path.append(bootstrap_path)

    TRACER.log('PYTHONPATH contains:')
    for element in sys.path:
      TRACER.log('  %c %s' % (' ' if os.path.exists(element) else '*', element))
    TRACER.log('  * - paths that do not exist or will be imported via zipimport')