  def GetRootKey(self):
    """Retrieves the root keys.

    Returns:
      A Registry key (instance of WinRegistryKey) or None if not available.
    """
    regf_key = self._regf_file.get_root_key()
    if not regf_key:
      return

    # TODO: refactor to WinRegistryKey, also remove parent key path or
    # use WinRegistry path.
    return WinPyregfKey(regf_key, u'', root=True)