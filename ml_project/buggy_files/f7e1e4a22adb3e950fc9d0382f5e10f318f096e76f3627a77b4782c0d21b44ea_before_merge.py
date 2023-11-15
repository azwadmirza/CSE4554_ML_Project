  def _ParseRecord(self, parser_mediator, file_object):
    """Parses an event record.

    Args:
      parser_mediator (ParserMediator): mediates interactions between parsers
          and other components, such as storage and dfvfs.
      file_object (dfvfs.FileIO): file-like object.

    Raises:
      ParseError: if the event record cannot be read.
    """
    header_record_offset = file_object.tell()

    # Check the header token type before reading the token data to prevent
    # variable size tokens to consume a large amount of memory.
    token_type = self._ParseTokenType(file_object, header_record_offset)
    if token_type not in self._HEADER_TOKEN_TYPES:
      raise errors.ParseError(
          'Unsupported header token type: 0x{0:02x}'.format(token_type))

    token_type, token_data = self._ParseToken(file_object, header_record_offset)

    if token_data.format_version != 11:
      raise errors.ParseError('Unsupported format version type: {0:d}'.format(
          token_data.format_version))

    timestamp = token_data.microseconds + (
        token_data.timestamp * definitions.MICROSECONDS_PER_SECOND)

    event_type = token_data.event_type
    header_record_size = token_data.record_size
    record_end_offset = header_record_offset + header_record_size

    event_tokens = []
    return_token_values = None

    file_offset = file_object.tell()
    while file_offset < record_end_offset:
      token_type, token_data = self._ParseToken(file_object, file_offset)
      if not token_data:
        raise errors.ParseError('Unsupported token type: 0x{0:02x}'.format(
            token_type))

      file_offset = file_object.tell()

      if token_type == self._TOKEN_TYPE_AUT_TRAILER:
        break

      token_type_string = self._TOKEN_TYPES.get(token_type, 'UNKNOWN')
      token_values = self._FormatTokenData(token_type, token_data)
      event_tokens.append({token_type_string: token_values})

      if token_type in (
          self._TOKEN_TYPE_AUT_RETURN32, self._TOKEN_TYPE_AUT_RETURN64):
        return_token_values = token_values

    if token_data.signature != self._TRAILER_TOKEN_SIGNATURE:
      raise errors.ParseError('Unsupported signature in trailer token.')

    if token_data.record_size != header_record_size:
      raise errors.ParseError(
          'Mismatch of event record size between header and trailer token.')

    event_data = BSMEventData()
    event_data.event_type = event_type
    event_data.extra_tokens = event_tokens
    event_data.offset = header_record_offset
    event_data.record_length = header_record_size
    event_data.return_value = return_token_values

    date_time = dfdatetime_posix_time.PosixTimeInMicroseconds(
        timestamp=timestamp)
    event = time_events.DateTimeValuesEvent(
        date_time, definitions.TIME_DESCRIPTION_CREATION)
    parser_mediator.ProduceEventWithEventData(event, event_data)