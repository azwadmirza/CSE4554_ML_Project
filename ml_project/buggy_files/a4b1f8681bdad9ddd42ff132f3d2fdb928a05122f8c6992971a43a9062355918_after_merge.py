  def WriteInitialize(self):
    """Initializes the write of a serialized data stream.

    Creates a temporary file to store the serialized data.

    Returns:
      int: offset of the entry within the temporary file.

    Raises:
      IOError: if the serialized data stream cannot be written.
    """
    stream_file_path = os.path.join(self._path, self._stream_name)
    self._file_object = open(stream_file_path, 'wb')
    if platform_specific.PlatformIsWindows():
      file_handle = self._file_object.fileno()
      platform_specific.DisableWindowsFileHandleInheritance(file_handle)
    return self._file_object.tell()