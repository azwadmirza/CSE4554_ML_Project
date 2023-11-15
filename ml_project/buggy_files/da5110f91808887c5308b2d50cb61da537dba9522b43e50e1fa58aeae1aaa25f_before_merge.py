  def ProcessSource(self):
    """Processes the source.

    Args:
      options: the command line arguments (instance of argparse.Namespace).

    Raises:
      SourceScannerError: if the source scanner could not find a supported
                          file system.
      UserAbort: if the user initiated an abort.
    """
    self._front_end.SetEnableProfiling(
        self._enable_profiling,
        profiling_sample_rate=self._profiling_sample_rate,
        profiling_type=self._profiling_type)
    self._front_end.SetStorageFile(self._output)
    self._front_end.SetShowMemoryInformation(show_memory=self._foreman_verbose)

    self._front_end.ScanSource(
        self._source_path, partition_number=self._partition_number,
        partition_offset=self._partition_offset, enable_vss=self._process_vss,
        vss_stores=self._vss_stores)

    self._output_writer.Write(u'\n')
    self.PrintOptions()

    # TODO: merge this into the output of PrintOptions.
    self._DebugPrintCollection()

    logging.info(u'Processing started.')

    if self._status_view_mode == u'linear':
      status_update_callback = self._PrintStatusUpdateStream
    elif self._status_view_mode == u'window':
      status_update_callback = self._PrintStatusUpdate
    else:
      status_update_callback = None

    self._front_end.ProcessSource(
        filter_file=self._filter_file,
        hasher_names_string=self._hasher_names_string,
        parser_filter_string=self._parser_filter_string,
        single_process_mode=self._single_process_mode,
        status_update_callback=status_update_callback,
        storage_serializer_format=self._storage_serializer_format,
        timezone=self._timezone)

    logging.info(u'Processing completed.')