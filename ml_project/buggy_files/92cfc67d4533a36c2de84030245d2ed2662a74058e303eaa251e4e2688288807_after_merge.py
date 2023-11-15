  def _Open(self, path, access_mode='r'):
    """Opens the storage file.

    Args:
      path: string containing the path of the storage file.
      access_mode: optional string indicating the access mode.

    Raises:
      IOError: if the ZIP file is already opened or if the ZIP file cannot
               be opened.
    """
    if self._zipfile:
      raise IOError(u'ZIP file already opened.')

    self._path = path

    try:
      self._zipfile = zipfile.ZipFile(
          self._path, mode=access_mode, compression=zipfile.ZIP_DEFLATED,
          allowZip64=True)

    except zipfile.BadZipfile as exception:
      raise IOError(
          u'Unable to open ZIP file with error: {0:s}'.format(exception))