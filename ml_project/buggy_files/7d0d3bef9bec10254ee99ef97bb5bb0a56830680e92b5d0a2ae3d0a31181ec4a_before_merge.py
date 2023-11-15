  def ParseOptions(cls, options, analysis_plugin):
    """Parses and validates options.

    Args:
      options (argparse.Namespace): parser options.
      analysis_plugin (VirusTotalAnalysisPlugin): analysis plugin to configure.

    Raises:
      BadConfigObject: when the output module object is of the wrong type.
      BadConfigOption: when a configuration parameter fails validation.
    """
    if not isinstance(analysis_plugin, virustotal.VirusTotalAnalysisPlugin):
      raise errors.BadConfigObject(
          u'Analysis plugin is not an instance of VirusTotalAnalysisPlugin')

    api_key = cls._ParseStringOption(options, u'virustotal_api_key')
    if not api_key:
      raise errors.BadConfigOption(
          u'VirusTotal API key not specified. Try again with '
          u'--virustotal-api-key.')

    analysis_plugin.SetAPIKey(api_key)

    rate_limit = getattr(
        options, u'virustotal_rate_limit', cls._DEFAULT_RATE_LIMIT)
    analysis_plugin.EnableFreeAPIKeyRateLimit(rate_limit)