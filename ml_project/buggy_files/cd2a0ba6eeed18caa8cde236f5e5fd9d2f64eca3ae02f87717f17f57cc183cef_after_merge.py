  def ParseFileObject(self, parser_mediator, file_object):
    """Parses a CUPS IPP file-like object.

    Args:
      parser_mediator (ParserMediator): mediates interactions between parsers
          and other components, such as storage and dfvfs.
      file_object (dfvfs.FileIO): file-like object.

    Raises:
      UnableToParseFile: when the file cannot be parsed.
    """
    self._last_charset_attribute = 'ascii'

    self._ParseHeader(parser_mediator, file_object)

    data_dict = {}
    time_dict = {}
    is_first_attribute_group = True

    try:
      for name, value in self._ParseAttributesGroup(file_object):
        name = self._ATTRIBUTE_NAME_TRANSLATION.get(name, name)

        if name in self._DATE_TIME_VALUE_NAMES:
          time_dict.setdefault(name, []).append(value)
        else:
          data_dict.setdefault(name, []).append(value)

        is_first_attribute_group = False

    except (ValueError, errors.ParseError) as exception:
      error_message = (
          'unable to parse attribute group with error: {0!s}').format(exception)
      if is_first_attribute_group:
        raise errors.UnableToParseFile(error_message)

      parser_mediator.ProduceExtractionWarning(error_message)
      return

    event_data = CupsIppEventData()
    event_data.application = self._GetStringValue(data_dict, 'application')
    event_data.computer_name = self._GetStringValue(data_dict, 'computer_name')
    event_data.copies = data_dict.get('copies', [0])[0]
    event_data.doc_type = self._GetStringValue(data_dict, 'doc_type')
    event_data.job_id = self._GetStringValue(data_dict, 'job_id')
    event_data.job_name = self._GetStringValue(data_dict, 'job_name')
    event_data.user = self._GetStringValue(data_dict, 'user')
    event_data.owner = self._GetStringValue(data_dict, 'owner')
    event_data.printer_id = self._GetStringValue(data_dict, 'printer_id')
    event_data.uri = self._GetStringValue(data_dict, 'uri')

    for name, usage in iter(self._DATE_TIME_VALUES.items()):
      for date_time in time_dict.get(name, []):
        event = time_events.DateTimeValuesEvent(date_time, usage)
        parser_mediator.ProduceEventWithEventData(event, event_data)

    for name, usage in iter(self._POSIX_TIME_VALUES.items()):
      for time_value in time_dict.get(name, []):
        date_time = dfdatetime_posix_time.PosixTime(timestamp=time_value)
        event = time_events.DateTimeValuesEvent(date_time, usage)
        parser_mediator.ProduceEventWithEventData(event, event_data)