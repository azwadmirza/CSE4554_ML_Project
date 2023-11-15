  def SetFilePath(self, file_path):
    """Sets the file-like object based on the file path.

    Args:
      file_path: the full path to the output file.
    """
    self._file_object = open(file_path, 'wb')