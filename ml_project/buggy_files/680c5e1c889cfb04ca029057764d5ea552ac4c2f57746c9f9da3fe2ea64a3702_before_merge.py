  def _ProcessDataStreams(self, file_entry):
    """Processes the data streams in a file entry.

    Args:
      file_entry: a file entry (instance of dfvfs.FileEntry).
    """
    produced_main_path_spec = False
    for data_stream in file_entry.data_streams:
      # Make a copy so we don't make the changes on a path specification
      # directly. Otherwise already produced path specifications can be
      # altered in the process.
      path_spec = copy.deepcopy(file_entry.path_spec)
      setattr(path_spec, u'data_stream', data_stream.name)
      self.ProduceItem(path_spec)

      if not data_stream.name:
        produced_main_path_spec = True

    if (not produced_main_path_spec and (
        not file_entry.IsDirectory() or self._collect_directory_metadata)):
      self.ProduceItem(file_entry.path_spec)