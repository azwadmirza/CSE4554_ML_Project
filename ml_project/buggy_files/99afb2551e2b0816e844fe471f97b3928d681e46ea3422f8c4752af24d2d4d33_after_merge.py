  def RecurseKeys(self):
    """Recurses the Registry file keys starting with the root key.

    Yields:
      A Registry key (instance of WinPyregfKey) generator.

    Raises:
      StopIteration: when there is no root key to signal the generator is empty.
    """
    root_key = self.GetRootKey()
    if not root_key:
      raise StopIteration

    for key in self._RecurseKey(root_key):
      yield key