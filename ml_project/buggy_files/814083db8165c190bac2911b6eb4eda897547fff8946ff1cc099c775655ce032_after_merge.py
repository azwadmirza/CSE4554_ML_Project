  def ParseRecord(self, parser_mediator, key, structure):
    """Parses a structure of tokens derived from a line of a text file.

    Args:
      parser_mediator (ParserMediator): parser mediator.
      key (str): identifier of the structure of tokens.
      structure (pyparsing.ParseResults): structure of tokens derived from
          a line of a text file.

    Raises:
      ParseError: when the structure type is unknown.
    """
    if key != u'line':
      raise errors.ParseError(
          u'Unable to parse record, unknown structure: {0:s}'.format(key))

    msg_value = structure.get(u'msg')
    if not msg_value:
      parser_mediator.ProduceExtractionError(
          u'missing msg value: {0!s}'.format(structure))
      return

    try:
      seconds = int(msg_value[0], 10)
    except ValueError:
      parser_mediator.ProduceExtractionError(
          u'unsupported number of seconds in msg value: {0!s}'.format(
              structure))
      return

    try:
      milliseconds = int(msg_value[1], 10)
    except ValueError:
      parser_mediator.ProduceExtractionError(
          u'unsupported number of milliseconds in msg value: {0!s}'.format(
              structure))
      return

    timestamp = ((seconds * 1000) + milliseconds) * 1000
    body_text = structure[2][0]

    try:
      # Try to parse the body text as key value pairs. Note that not
      # all log lines will be properly formatted key value pairs.
      key_value_dict = self._SELINUX_KEY_VALUE_DICT.parseString(body_text)
    except pyparsing.ParseException:
      key_value_dict = {}

    audit_type = structure.get(u'type')
    pid = key_value_dict.get(u'pid')

    event_object = SELinuxLineEvent(timestamp, 0, audit_type, pid, body_text)
    parser_mediator.ProduceEvent(event_object)