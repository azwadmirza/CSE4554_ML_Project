  def __init__(self, source_dir, interpreter=None, install_dir=None):
    """Create an installer from an unpacked source distribution in source_dir."""
    self._source_dir = source_dir
    self._install_tmp = install_dir or safe_mkdtemp()
    self._installed = None

    from pex import vendor
    self._interpreter = vendor.setup_interpreter(distributions=self.mixins,
                                                 interpreter=interpreter or PythonInterpreter.get())
    if not self._interpreter.satisfies(self.mixins):
      raise self.IncapableInterpreter('Interpreter %s not capable of running %s' % (
          self._interpreter.binary, self.__class__.__name__))