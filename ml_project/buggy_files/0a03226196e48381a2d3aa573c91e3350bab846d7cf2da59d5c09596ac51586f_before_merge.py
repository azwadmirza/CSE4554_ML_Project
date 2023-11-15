  def run(self):
    parser, options_builder = configure_clp()
    options, reqs = parser.parse_args(self.pex_args)

    if options.entry_point or options.script or options.pex_name:
      die('Must not specify entry point, script or output file to --pex-args, given: {}'
          .format(' '.join(self.pex_args)))

    name = self.distribution.get_name()
    version = self.distribution.get_version()

    package_dir = os.path.dirname(os.path.realpath(os.path.expanduser(
      self.distribution.script_name)))
    if self.bdist_dir is None:
      self.bdist_dir = os.path.join(package_dir, 'dist')

    console_scripts = self.parse_entry_points()

    pex_specs = []
    if self.bdist_all:
      # Write all entry points into unversioned pex files.
      pex_specs.extend((script_name, os.path.join(self.bdist_dir, script_name))
                       for script_name in console_scripts)
    else:
      target = os.path.join(self.bdist_dir, name + '-' + version + '.pex')
      pex_specs.append((name if name in console_scripts else None, target))

    # In order for code to run to here, pex is on the sys.path - make sure to propagate the
    # sys.path so the subprocess can find us.
    env = os.environ.copy()
    env['PYTHONPATH'] = os.pathsep.join(sys.path)

    args = [sys.executable, '-s', '-m', 'pex.bin.pex', package_dir] + reqs + self.pex_args
    if self.get_log_level() < log.INFO and options.verbosity == 0:
      args.append('-v')

    for script_name, target in pex_specs:
      cmd = args + ['--output-file', target]
      if script_name:
        log.info('Writing %s to %s' % (script_name, target))
        cmd += ['--script', script_name]
      else:
        # The package has no namesake entry point, so build an environment pex.
        log.info('Writing environment pex into %s' % target)

      log.debug('Building pex via: {}'.format(' '.join(cmd)))
      process = Executor.open_process(cmd, env=env)
      _, stderr = process.communicate()
      result = process.returncode
      if result != 0:
        die('Failed to create pex via {}:\n{}'.format(' '.join(cmd), stderr), result)