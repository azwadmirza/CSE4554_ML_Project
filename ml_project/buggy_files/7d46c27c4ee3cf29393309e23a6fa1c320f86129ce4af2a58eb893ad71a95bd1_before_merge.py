  def __init__(self, binary, identity, extras=None):
    """Construct a PythonInterpreter.

       You should probably PythonInterpreter.from_binary instead.

       :param binary: The full path of the python binary.
       :param identity: The :class:`PythonIdentity` of the PythonInterpreter.
       :param extras: A mapping from (dist.key, dist.version) to dist.location
                      of the extras associated with this interpreter.
    """
    self._binary = os.path.realpath(binary)
    self._extras = extras or {}
    self._identity = identity