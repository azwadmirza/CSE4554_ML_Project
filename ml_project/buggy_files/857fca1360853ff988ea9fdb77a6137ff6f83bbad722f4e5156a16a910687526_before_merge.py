  def ParseOptions(cls, options, analysis_plugin):
    """Parses and validates options.

    Args:
      options (argparse.Namespace): parser options object.
      analysis_plugin (NsrlsvrAnalysisPlugin): analysis plugin to configure.

    Raises:
      BadConfigObject: when the analysis plugin is the wrong type.
    """
    if not isinstance(analysis_plugin, nsrlsvr.NsrlsvrAnalysisPlugin):
      raise errors.BadConfigObject(
          u'Analysis plugin is not an instance of NsrlsvrAnalysisPlugin')

    host = cls._ParseStringOption(
        options, u'nsrlsvr_host', default_value=cls._DEFAULT_HOST)
    analysis_plugin.SetHost(host)

    port = cls._ParseStringOption(
        options, u'nsrlsvr_port', default_value=cls._DEFAULT_PORT)
    analysis_plugin.SetPort(port)