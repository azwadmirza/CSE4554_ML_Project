  def expose(self):
    self._exposed = True
    importlib.import_module(self.module)
    _tracer().log('Exposed {}'.format(self), V=3)