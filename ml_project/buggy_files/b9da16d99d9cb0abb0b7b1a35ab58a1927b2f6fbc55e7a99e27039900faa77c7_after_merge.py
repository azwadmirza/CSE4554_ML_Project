  def _ProcessFileEntryDataStream(
      self, parser_mediator, file_entry, data_stream_name):
    """Processes a specific data stream of a file entry.

    Args:
      parser_mediator (ParserMediator): parser mediator.
      file_entry (dfvfs.FileEntry): file entry containing the data stream.
      data_stream_name (str): data stream name.
    """
    # Not every file entry has a data stream. In such cases we want to
    # extract the metadata only.
    has_data_stream = file_entry.HasDataStream(data_stream_name)
    if has_data_stream:
      self._HashDataStream(parser_mediator, file_entry, data_stream_name)

    # We always want to extract the file entry metadata but we only want
    # to parse it once per file entry, so we only use it if we are
    # processing the default (nameless) data stream.
    if (not data_stream_name and (
        not file_entry.IsRoot() or
        file_entry.type_indicator in self._TYPES_WITH_ROOT_METADATA)):
      self._ExtractMetadataFromFileEntry(parser_mediator, file_entry)

    # Determine if the content of the file entry should not be extracted.
    skip_content_extraction = self._CanSkipContentExtraction(file_entry)
    if skip_content_extraction:
      display_name = parser_mediator.GetDisplayName()
      logging.info(
          u'Skipping content extraction of: {0:s}'.format(display_name))
      return

    if not has_data_stream:
      if file_entry.IsDirectory():
        self._ProcessDirectory(parser_mediator, file_entry)

    else:
      path_spec = copy.deepcopy(file_entry.path_spec)
      if data_stream_name:
        path_spec.data_stream = data_stream_name

      archive_types = []
      compressed_stream_types = []

      compressed_stream_types = self._GetCompressedStreamTypes(
          parser_mediator, path_spec)

      if not compressed_stream_types:
        archive_types = self._GetArchiveTypes(parser_mediator, path_spec)

      if archive_types:
        if self._process_archive_files:
          self._ProcessArchiveTypes(parser_mediator, path_spec, archive_types)

        if dfvfs_definitions.TYPE_INDICATOR_ZIP in archive_types:
          self.processing_status = definitions.PROCESSING_STATUS_EXTRACTING

          # ZIP files are the base of certain file formats like docx.
          self._event_extractor.ParseDataStream(
              parser_mediator, file_entry, data_stream_name)

      elif compressed_stream_types:
        self._ProcessCompressedStreamTypes(
            parser_mediator, path_spec, compressed_stream_types)

      else:
        self.processing_status = definitions.PROCESSING_STATUS_EXTRACTING

        self._event_extractor.ParseDataStream(
            parser_mediator, file_entry, data_stream_name)