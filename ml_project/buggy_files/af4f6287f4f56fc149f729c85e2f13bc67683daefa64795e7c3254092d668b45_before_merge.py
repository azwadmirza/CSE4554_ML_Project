  def CreateSession(
      self, command_line_arguments=None, filter_file=None,
      parser_filter_expression=None, preferred_encoding=u'utf-8',
      preferred_year=None):
    """Creates a session attribute containiner.

    Args:
      command_line_arguments (Optional[str]): the command line arguments.
      filter_file (Optional[str]): path to a file with find specifications.
      parser_filter_expression (Optional[str]): parser filter expression.
      preferred_encoding (Optional[str]): preferred encoding.
      preferred_year (Optional[int]): preferred year.

    Returns:
      Session: session attribute container.
    """
    session = sessions.Session()

    parser_and_plugin_names = [
        parser_name for parser_name in (
            parsers_manager.ParsersManager.GetParserAndPluginNames(
                parser_filter_expression=parser_filter_expression))]

    session.command_line_arguments = command_line_arguments
    session.enabled_parser_names = parser_and_plugin_names
    session.filter_expression = self._filter_expression
    session.filter_file = filter_file
    session.debug_mode = self._debug_mode
    session.parser_filter_expression = parser_filter_expression
    session.preferred_encoding = preferred_encoding
    session.preferred_year = preferred_year

    return session