  def run(self):
    if self._installed is not None:
      return self._installed

    with TRACER.timed('Installing %s' % self._install_tmp, V=2):
      env = self._interpreter.sanitized_environment()
      mixins = OrderedSet(['setuptools'] + self.mixins)
      env['PYTHONPATH'] = os.pathsep.join(third_party.expose(mixins))
      env['__PEX_UNVENDORED__'] = '1'

      command = [self._interpreter.binary, '-s', '-'] + self.setup_command()
      try:
        Executor.execute(command,
                         env=env,
                         cwd=self._source_dir,
                         stdin_payload=self.setup_py_wrapper.encode('ascii'))
        self._installed = True
      except Executor.NonZeroExit as e:
        self._installed = False
        name = os.path.basename(self._source_dir)
        print('**** Failed to install %s (caused by: %r\n):' % (name, e), file=sys.stderr)
        print('stdout:\n%s\nstderr:\n%s\n' % (e.stdout, e.stderr), file=sys.stderr)
        return self._installed

    return self._installed