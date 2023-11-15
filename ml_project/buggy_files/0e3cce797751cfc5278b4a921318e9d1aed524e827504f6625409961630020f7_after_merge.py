  def __init__(self, source_dir, interpreter=None, install_dir=None):
    """Create an installer from an unpacked source distribution in source_dir."""
    self._source_dir = source_dir
    self._install_tmp = install_dir or safe_mkdtemp()
    self._interpreter = interpreter or PythonInterpreter.get()
    self._installed = None