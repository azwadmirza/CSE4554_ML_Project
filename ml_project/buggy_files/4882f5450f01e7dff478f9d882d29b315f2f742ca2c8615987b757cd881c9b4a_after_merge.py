  def demote_bootstrap(cls):
    TRACER.log('Bootstrap complete, performing final sys.path modifications...')

    should_log = {level: TRACER.should_log(V=level) for level in range(1, 10)}

    def log(msg, V=1):
      if should_log.get(V, False):
        print('pex: {}'.format(msg), file=sys.stderr)

    # Remove the third party resources pex uses and demote pex bootstrap code to the end of
    # sys.path for the duration of the run to allow conflicting versions supplied by user
    # dependencies to win during the course of the execution of user code.
    unregister_finders()
    third_party.uninstall()

    bootstrap = Bootstrap.locate()
    log('Demoting code from %s' % bootstrap, V=2)
    for module in bootstrap.demote():
      log('un-imported {}'.format(module), V=9)

    import pex
    log('Re-imported pex from {}'.format(pex.__path__), V=3)

    log('PYTHONPATH contains:')
    for element in sys.path:
      log('  %c %s' % (' ' if os.path.exists(element) else '*', element))
    log('  * - paths that do not exist or will be imported via zipimport')