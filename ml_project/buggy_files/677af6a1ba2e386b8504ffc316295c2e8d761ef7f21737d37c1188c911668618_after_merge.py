  def _OpenZIPFile(self, path, read_only):
    """Opens the ZIP file.

    Args:
      path (str): path of the ZIP file.
      read_only (bool): True if the file should be opened in read-only mode.

    Raises:
      IOError: if the ZIP file is already opened or if the ZIP file cannot
               be opened.
    """
    if self._zipfile:
      raise IOError(u'ZIP file already opened.')

    if read_only:
      access_mode = 'r'

      zipfile_path = path
    else:
      access_mode = 'a'

      # Create a temporary directory to prevent multiple ZIP storage
      # files in the same directory conflicting with each other.
      directory_name = os.path.dirname(path)
      basename = os.path.basename(path)
      directory_name = tempfile.mkdtemp(dir=directory_name)
      zipfile_path = os.path.join(directory_name, basename)

      if os.path.exists(path):
        attempts = 1
        # On Windows the file can sometimes be in use and we have to wait.
        while attempts <= self._MAXIMUM_NUMBER_OF_LOCKED_FILE_RETRIES:
          try:
            os.rename(path, zipfile_path)
            break

          except OSError:
            if attempts == self._MAXIMUM_NUMBER_OF_LOCKED_FILE_RETRIES:
              raise
            time.sleep(self._LOCKED_FILE_SLEEP_TIME)
            attempts += 1

    try:
      self._zipfile = zipfile.ZipFile(
          zipfile_path, mode=access_mode, compression=zipfile.ZIP_DEFLATED,
          allowZip64=True)
      self._zipfile_path = zipfile_path
      if platform_specific.PlatformIsWindows():
        file_handle = self._zipfile.fp.fileno()
        platform_specific.DisableWindowsFileHandleInheritance(file_handle)

    except zipfile.BadZipfile as exception:
      raise IOError(u'Unable to open ZIP file: {0:s} with error: {1:s}'.format(
          zipfile_path, exception))

    self._is_open = True
    self._path = path
    self._read_only = read_only