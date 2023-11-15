  def __init__(self, binary, identity):
    """Construct a PythonInterpreter.

       You should probably PythonInterpreter.from_binary instead.

       :param binary: The full path of the python binary.
       :param identity: The :class:`PythonIdentity` of the PythonInterpreter.
    """
    self._binary = os.path.realpath(binary)
    self._identity = identity