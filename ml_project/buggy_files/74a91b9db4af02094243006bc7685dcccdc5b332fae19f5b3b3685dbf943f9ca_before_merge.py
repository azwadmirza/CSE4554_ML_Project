  def ParseOptions(self, options):
    """Parses the options.

    Args:
      options: the command line arguments (instance of argparse.Namespace).

    Raises:
      BadConfigOption: if the options are invalid.
    """
    # Check the list options first otherwise required options will raise.
    self._ParseLanguageOptions(options)
    self._ParseTimezoneOption(options)

    if (self.list_analysis_plugins or self.list_language_identifiers or
        self.list_output_modules or self.list_timezones):
      return

    super(PsortTool, self).ParseOptions(options)
    self._ParseDataLocationOption(options)
    self._ParseAnalysisPluginOptions(options)
    self._ParseFilterOptions(options)

    if self._debug_mode:
      logging_level = logging.DEBUG
    elif self._quiet_mode:
      logging_level = logging.WARNING
    else:
      logging_level = logging.INFO

    log_file = getattr(options, u'log_file', None)
    self._ConfigureLogging(log_level=logging_level, filename=log_file)

    self._output_format = getattr(options, u'output_format', None)
    if not self._output_format:
      raise errors.BadConfigOption(u'Missing output format.')
    self._front_end.SetOutputFormat(self._output_format)

    if not self._front_end.HasOutputClass(self._output_format):
      raise errors.BadConfigOption(
          u'Unsupported output format: {0:s}.'.format(self._output_format))

    self._deduplicate_events = getattr(options, u'dedup', True)

    self._output_filename = getattr(options, u'write', None)
    if self._output_filename:
      self._front_end.SetOutputFilename(self._output_filename)

    if not self._data_location:
      logging.warning(u'Unable to automatically determine data location.')

    # TODO: refactor this.
    self._options = options