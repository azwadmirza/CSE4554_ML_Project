  def RecurseKeys(self):
    """Recurses the Registry file keys starting with the root key.

    Yields:
      A Registry key (instance of WinPyregfKey) generator.
    """
    root_key = self.GetRootKey()
    return self._RecurseKey(root_key)