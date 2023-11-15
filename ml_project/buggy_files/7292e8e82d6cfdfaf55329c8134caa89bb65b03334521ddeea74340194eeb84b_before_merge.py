  def ProcessSources(
      self, source_path_specs, storage_writer, resolver_context,
      processing_configuration, filter_find_specs=None,
      status_update_callback=None):
    """Processes the sources.

    Args:
      source_path_specs (list[dfvfs.PathSpec]): path specifications of
          the sources to process.
      storage_writer (StorageWriter): storage writer for a session storage.
      resolver_context (dfvfs.Context): resolver context.
      processing_configuration (ProcessingConfiguration): processing
          configuration.
      filter_find_specs (Optional[list[dfvfs.FindSpec]]): find specifications
          used in path specification extraction.
      status_update_callback (Optional[function]): callback function for status
          updates.

    Returns:
      ProcessingStatus: processing status.
    """
    parser_mediator = parsers_mediator.ParserMediator(
        storage_writer, self.knowledge_base,
        preferred_year=processing_configuration.preferred_year,
        resolver_context=resolver_context,
        temporary_directory=processing_configuration.temporary_directory)

    parser_mediator.SetEventExtractionConfiguration(
        processing_configuration.event_extraction)

    parser_mediator.SetInputSourceConfiguration(
        processing_configuration.input_source)

    extraction_worker = worker.EventExtractionWorker(
        parser_filter_expression=(
            processing_configuration.parser_filter_expression))

    extraction_worker.SetExtractionConfiguration(
        processing_configuration.extraction)

    self._status_update_callback = status_update_callback

    logging.debug(u'Processing started.')

    self._StartProfiling(extraction_worker)

    if self._serializers_profiler:
      storage_writer.SetSerializersProfiler(self._serializers_profiler)

    storage_writer.Open()
    storage_writer.WriteSessionStart()

    try:
      storage_writer.WritePreprocessingInformation(self.knowledge_base)

      self._ProcessSources(
          source_path_specs, extraction_worker, parser_mediator,
          storage_writer, filter_find_specs=filter_find_specs)

    finally:
      storage_writer.WriteSessionCompletion(aborted=self._abort)

      storage_writer.Close()

      if self._serializers_profiler:
        storage_writer.SetSerializersProfiler(None)

      self._StopProfiling(extraction_worker)

    if self._abort:
      logging.debug(u'Processing aborted.')
      self._processing_status.aborted = True
    else:
      logging.debug(u'Processing completed.')

    self._status_update_callback = None

    return self._processing_status