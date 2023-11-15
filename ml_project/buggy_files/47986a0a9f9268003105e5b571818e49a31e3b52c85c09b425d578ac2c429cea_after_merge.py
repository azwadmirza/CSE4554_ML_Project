  def Match(self, registry_key):
    """Determines if a Windows Registry key matches the filter.

    Args:
      registry_key: a Windows Registry key (instance of
                    dfwinreg.WinRegistryKey).

    Returns:
      A boolean value that indicates a match.
    """
    key_path_upper = registry_key.path.upper()
    # Prevent this filter matching non-string MRUListEx values.
    for ignore_key_path_suffix in self._IGNORE_KEY_PATH_SUFFIXES:
      if key_path_upper.endswith(ignore_key_path_suffix):
        return False

    for ignore_key_path_segment in self._IGNORE_KEY_PATH_SEGMENTS:
      if ignore_key_path_segment in key_path_upper:
        return False

    return super(MRUListExStringRegistryKeyFilter, self).Match(registry_key)