  def GetRootKey(self):
    """Retrieves the root keys.

    Yields:
      A Registry key (instance of WinRegistryKey).
    """
    regf_key = self._regf_file.get_root_key()
    return WinPyregfKey(regf_key, u'', root=True)