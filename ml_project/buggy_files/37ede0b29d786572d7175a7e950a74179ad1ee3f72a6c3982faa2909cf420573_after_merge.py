  def function_wrapper(self, *args, **kw):
    self._installed = self.run()
    if not self._installed:
      raise SetuptoolsInstallerBase.InstallFailure('Failed to install %s' % self._source_dir)
    return function(self, *args, **kw)