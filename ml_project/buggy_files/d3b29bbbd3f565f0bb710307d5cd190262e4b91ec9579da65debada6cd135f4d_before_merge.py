  def run(self):
    if self._installed is not None:
      return self._installed

    with TRACER.timed('Installing %s' % self._install_tmp, V=2):
      command = [self._interpreter.binary, '-sE', '-'] + self._setup_command()
      try:
        Executor.execute(command,
                         env=self._interpreter.sanitized_environment(),
                         cwd=self._source_dir,
                         stdin_payload=self.bootstrap_script.encode('ascii'))
        self._installed = True
      except Executor.NonZeroExit as e:
        self._installed = False
        name = os.path.basename(self._source_dir)
        print('**** Failed to install %s (caused by: %r\n):' % (name, e), file=sys.stderr)
        print('stdout:\n%s\nstderr:\n%s\n' % (e.stdout, e.stderr), file=sys.stderr)
        return self._installed

    return self._installed