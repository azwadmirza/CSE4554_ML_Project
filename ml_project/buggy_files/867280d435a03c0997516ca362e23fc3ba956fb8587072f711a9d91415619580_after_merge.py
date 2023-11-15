  def ProcessStorage(self):
    """Processes a plaso storage file.

    Raises:
      BadConfigOption: when a configuration parameter fails validation.
      RuntimeError: if a non-recoverable situation is encountered.
    """
    output_module = self._front_end.CreateOutputModule(
        self._output_format, preferred_encoding=self.preferred_encoding,
        timezone=self._timezone)

    if isinstance(output_module, output_interface.LinearOutputModule):
      if not self._output_filename:
        # TODO: Remove "no longer supported" after 1.5 release.
        raise errors.BadConfigOption((
            u'Output format: {0:s} requires an output file, output to stdout '
            u'is no longer supported.').format(self._output_format))

      if self._output_filename and os.path.exists(self._output_filename):
        raise errors.BadConfigOption((
            u'Output file already exists: {0:s}. Aborting.').format(
                self._output_filename))

      output_file_object = open(self._output_filename, u'wb')
      output_writer = cli_tools.FileObjectOutputWriter(output_file_object)

      output_module.SetOutputWriter(output_writer)

    helpers_manager.ArgumentHelperManager.ParseOptions(
        self._options, output_module)

    # Check if there are parameters that have not been defined and need to
    # in order for the output module to continue. Prompt user to supply
    # those that may be missing.
    missing_parameters = output_module.GetMissingArguments()
    while missing_parameters:
      # TODO: refactor this.
      configuration_object = PsortOptions()
      setattr(configuration_object, u'output_format', output_module.NAME)
      for parameter in missing_parameters:
        value = self._PromptUserForInput(
            u'Missing parameter {0:s} for output module'.format(parameter))
        if value is None:
          logging.warning(
              u'Unable to set the missing parameter for: {0:s}'.format(
                  parameter))
          continue

        setattr(configuration_object, parameter, value)

      helpers_manager.ArgumentHelperManager.ParseOptions(
          configuration_object, output_module)
      missing_parameters = output_module.GetMissingArguments()

    analysis_plugins = self._front_end.GetAnalysisPlugins(
        self._analysis_plugins)
    for analysis_plugin in analysis_plugins:
      helpers_manager.ArgumentHelperManager.ParseOptions(
          self._options, analysis_plugin)

    if self._status_view_mode == u'linear':
      status_update_callback = self._PrintStatusUpdateStream
    elif self._status_view_mode == u'window':
      status_update_callback = self._PrintStatusUpdate
    else:
      status_update_callback = None

    session = self._front_end.CreateSession(
        command_line_arguments=self._command_line_arguments,
        preferred_encoding=self.preferred_encoding)

    storage_reader = self._front_end.CreateStorageReader(
        self._storage_file_path)
    self._number_of_analysis_reports = (
        storage_reader.GetNumberOfAnalysisReports())
    storage_reader.Close()

    if analysis_plugins:
      storage_writer = self._front_end.CreateStorageWriter(
          session, self._storage_file_path)
      # TODO: handle errors.BadConfigOption

      self._front_end.AnalyzeEvents(
          storage_writer, analysis_plugins,
          status_update_callback=status_update_callback)

    counter = collections.Counter()
    if self._output_format != u'null':
      storage_reader = self._front_end.CreateStorageReader(
          self._storage_file_path)

      events_counter = self._front_end.ExportEvents(
          storage_reader, output_module,
          deduplicate_events=self._deduplicate_events,
          time_slice=self._time_slice, use_time_slicer=self._use_time_slicer)

      counter += events_counter

    for item, value in iter(session.analysis_reports_counter.items()):
      counter[item] = value

    if self._quiet_mode:
      return

    self._output_writer.Write(u'Processing completed.\n')

    table_view = cli_views.ViewsFactory.GetTableView(
        self._views_format_type, title=u'Counter')
    for element, count in counter.most_common():
      if not element:
        element = u'N/A'
      table_view.AddRow([element, count])
    table_view.Write(self._output_writer)

    storage_reader = self._front_end.CreateStorageReader(
        self._storage_file_path)
    self._PrintAnalysisReportsDetails(storage_reader)