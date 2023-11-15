  def execute(self):
    binary = self.require_single_root_target()
    if isinstance(binary, PythonBinary):
      # We can't throw if binary isn't a PythonBinary, because perhaps we were called on a
      # jvm_binary, in which case we have to no-op and let jvm_run do its thing.
      # TODO(benjy): Use MutexTask to coordinate this.

      pex = self.create_pex(binary.pexinfo)
      self.context.release_lock()
      with self.context.new_workunit(name='run', labels=[WorkUnitLabel.RUN]):
        args = []
        for arg in self.get_options().args:
          args.extend(safe_shlex_split(arg))
        args += self.get_passthru_args()
        po = pex.run(blocking=False, args=args)
        try:
          result = po.wait()
          if result != 0:
            msg = '{interpreter} {entry_point} {args} ... exited non-zero ({code})'.format(
                interpreter=pex.interpreter.binary,
                entry_point=binary.entry_point,
                args=' '.join(args),
                code=result)
            raise TaskError(msg, exit_code=result)
        except KeyboardInterrupt:
          po.send_signal(signal.SIGINT)
          raise