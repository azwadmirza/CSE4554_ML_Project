  def _ParseKeyWithPlugin(self, parser_mediator, registry_key, plugin_object):
    """Parses the Registry key with a specific plugin.

    Args:
      parser_mediator: a parser mediator object (instance of ParserMediator).
      registry_key: a Registry key object (instance of
                    dfwinreg.WinRegistryKey).
      plugin_object: a Windows Registry plugin object (instance of
                     WindowsRegistryPlugin).
    """
    try:
      plugin_object.UpdateChainAndProcess(parser_mediator, registry_key)
    except (IOError, dfwinreg_errors.WinRegistryValueError) as exception:
      parser_mediator.ProduceParseError(u'{0:s}'.format(exception))