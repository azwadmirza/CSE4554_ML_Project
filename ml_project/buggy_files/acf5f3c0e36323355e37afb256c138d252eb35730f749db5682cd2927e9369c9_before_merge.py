  def ProcessSource(self, options):
    """Processes the source.

    Args:
      options: the command line arguments (instance of argparse.Namespace).

    Raises:
      SourceScannerError: if the source scanner could not find a supported
                          file system.
      UserAbort: if the user initiated an abort.
    """
    self.ScanSource(options)

    self.PrintOptions(options, self._source_path)

    if self._partition_offset is None:
      self._preprocess = False

    else:
      # If we're dealing with a storage media image always run pre-processing.
      self._preprocess = True

    self._CheckStorageFile(self._storage_file_path)

    # No need to multi process when we're only processing a single file.
    if self._scan_context.source_type == self._scan_context.SOURCE_TYPE_FILE:
      # If we are only processing a single file we don't need more than a
      # single worker.
      # TODO: Refactor this use of using the options object.
      options.workers = 1
      self._single_process_mode = False

    if self._scan_context.source_type in [
        self._scan_context.SOURCE_TYPE_DIRECTORY]:
      # If we are dealing with a directory we would like to attempt
      # pre-processing.
      self._preprocess = True

    if self._single_process_mode:
      self._ProcessSourceSingleProcessMode(options)
    else:
      self._ProcessSourceMultiProcessMode(options)