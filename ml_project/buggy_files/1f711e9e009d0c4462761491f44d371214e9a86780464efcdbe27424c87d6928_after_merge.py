def _run():
  """
  To add additional paths to sys.path, add a block to the config similar to the following:
  [main]
  roots: ['src/python/pants_internal/test/',]
  """
  version = get_version()
  if len(sys.argv) == 2 and sys.argv[1] == _VERSION_OPTION:
    _do_exit(version)

  root_dir = get_buildroot()
  if not os.path.exists(root_dir):
    _exit_and_fail('PANTS_BUILD_ROOT does not point to a valid path: %s' % root_dir)

  if len(sys.argv) < 2 or (len(sys.argv) == 2 and sys.argv[1] in _HELP_ALIASES):
    _help(version, root_dir)

  command_class, command_args = _parse_command(root_dir, sys.argv[1:])

  parser = optparse.OptionParser(version=version)
  RcFile.install_disable_rc_option(parser)
  parser.add_option(_LOG_EXIT_OPTION,
                    action='store_true',
                    default=False,
                    dest='log_exit',
                    help = 'Log an exit message on success or failure.')

  config = Config.load()

  # TODO: This can be replaced once extensions are enabled with
  # https://github.com/pantsbuild/pants/issues/5
  roots = config.getlist('parse', 'roots', default=[])
  sys.path.extend(map(lambda root: os.path.join(root_dir, root), roots))

  # XXX(wickman) This should be in the command goal, not un pants_exe.py!
  run_tracker = RunTracker.from_config(config)
  report = initial_reporting(config, run_tracker)
  run_tracker.start(report)

  url = run_tracker.run_info.get_info('report_url')
  if url:
    run_tracker.log(Report.INFO, 'See a report at: %s' % url)
  else:
    run_tracker.log(Report.INFO, '(To run a reporting server: ./pants goal server)')

  command = command_class(run_tracker, root_dir, parser, command_args)
  try:
    if command.serialized():
      def onwait(pid):
        print('Waiting on pants process %s to complete' % _process_info(pid), file=sys.stderr)
        return True
      runfile = os.path.join(root_dir, '.pants.run')
      lock = Lock.acquire(runfile, onwait=onwait)
    else:
      lock = Lock.unlocked()
    try:
      result = command.run(lock)
      _do_exit(result)
    except KeyboardInterrupt:
      command.cleanup()
      raise
    finally:
      lock.release()
  finally:
    run_tracker.end()
    # Must kill nailguns only after run_tracker.end() is called, because there may still
    # be pending background work that needs a nailgun.
    if (hasattr(command.options, 'cleanup_nailguns') and command.options.cleanup_nailguns) \
        or config.get('nailgun', 'autokill', default=False):
      NailgunTask.killall(None)