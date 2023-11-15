  def _ProcessFileEntryDataStream(self, mediator, file_entry, data_stream):
    """Processes a specific data stream of a file entry.

    Args:
      mediator (ParserMediator): mediates the interactions between
          parsers and other components, such as storage and abort signals.
      file_entry (dfvfs.FileEntry): file entry containing the data stream.
      data_stream (dfvfs.DataStream): data stream or None if the file entry
          has no data stream.
    """
    display_name = mediator.GetDisplayName()
    data_stream_name = getattr(data_stream, 'name', '') or ''
    logging.debug((
        '[ProcessFileEntryDataStream] processing data stream: "{0:s}" of '
        'file entry: {1:s}').format(data_stream_name, display_name))

    mediator.ClearEventAttributes()

    if data_stream and self._analyzers:
      # Since AnalyzeDataStream generates event attributes it needs to be
      # called before producing events.
      self._AnalyzeDataStream(mediator, file_entry, data_stream.name)

    self._ExtractMetadataFromFileEntry(mediator, file_entry, data_stream)

    # Not every file entry has a data stream. In such cases we want to
    # extract the metadata only.
    if not data_stream:
      return

    # Determine if the content of the file entry should not be extracted.
    skip_content_extraction = self._CanSkipContentExtraction(file_entry)
    if skip_content_extraction:
      display_name = mediator.GetDisplayName()
      logging.debug(
          'Skipping content extraction of: {0:s}'.format(display_name))
      self.processing_status = definitions.PROCESSING_STATUS_IDLE
      return

    path_spec = copy.deepcopy(file_entry.path_spec)
    if data_stream:
      path_spec.data_stream = data_stream.name

    archive_types = []
    compressed_stream_types = []

    if self._process_compressed_streams:
      compressed_stream_types = self._GetCompressedStreamTypes(
          mediator, path_spec)

    if not compressed_stream_types:
      archive_types = self._GetArchiveTypes(mediator, path_spec)

    if archive_types:
      if self._process_archives:
        self._ProcessArchiveTypes(mediator, path_spec, archive_types)

      if dfvfs_definitions.TYPE_INDICATOR_ZIP in archive_types:
        # ZIP files are the base of certain file formats like docx.
        self._ExtractContentFromDataStream(
            mediator, file_entry, data_stream.name)

    elif compressed_stream_types:
      self._ProcessCompressedStreamTypes(
          mediator, path_spec, compressed_stream_types)

    else:
      self._ExtractContentFromDataStream(
          mediator, file_entry, data_stream.name)