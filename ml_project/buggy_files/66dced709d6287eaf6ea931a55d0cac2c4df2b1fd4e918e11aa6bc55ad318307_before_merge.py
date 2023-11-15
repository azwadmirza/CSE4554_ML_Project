  def GetDisplayNameForPathSpec(
      cls, path_spec, mount_path=None, text_prepend=None):
    """Retrieves the display name of a path specification.

    Args:
      path_spec (dfvfs.PathSpec): path specification.
      mount_path (Optional[str]): path where the file system that is used
          by the path specification is mounted, such as "/mnt/image". The
          mount path will be stripped from the absolute path defined by
          the path specification.
      text_prepend (Optional[str]): text to prepend.

    Returns:
      str: human readable version of the path specification or None.
    """
    if not path_spec:
      return None

    relative_path = cls.GetRelativePathForPathSpec(
        path_spec, mount_path=mount_path)
    if not relative_path:
      return path_spec.type_indicator

    if text_prepend:
      relative_path = '{0:s}{1:s}'.format(text_prepend, relative_path)

    path_type_indicator = path_spec.type_indicator

    parent_path_spec = path_spec.parent
    if parent_path_spec:
      if path_spec.type_indicator == (
          dfvfs_definitions.TYPE_INDICATOR_COMPRESSED_STREAM):
        path_type_indicator = path_spec.compression_method.upper()
        parent_path_spec = parent_path_spec.parent

      elif path_spec.type_indicator == dfvfs_definitions.TYPE_INDICATOR_GZIP:
        parent_path_spec = parent_path_spec.parent

    if parent_path_spec and parent_path_spec.type_indicator == (
        dfvfs_definitions.TYPE_INDICATOR_VSHADOW):
      store_index = getattr(path_spec.parent, 'store_index', None)
      if store_index is not None:
        return 'VSS{0:d}:{1:s}:{2:s}'.format(
            store_index + 1, path_spec.type_indicator, relative_path)

    return '{0:s}:{1:s}'.format(path_type_indicator, relative_path)