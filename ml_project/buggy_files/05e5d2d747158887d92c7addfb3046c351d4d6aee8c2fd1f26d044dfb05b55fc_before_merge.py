  def ReadBSMEvent(self, parser_mediator, file_object):
    """Returns a BsmEvent from a single BSM entry.

    Args:
      parser_mediator: A parser mediator object (instance of ParserMediator).
      file_object: A file-like object.

    Returns:
      An event object.
    """
    # A list of tokens that has the entry.
    extra_tokens = []

    offset = file_object.tell()

    # Token header, first token for each entry.
    try:
      token_id = self.BSM_TYPE.parse_stream(file_object)
    except (IOError, construct.FieldError):
      return

    bsm_type, structure = self.BSM_TYPE_LIST.get(token_id, [u'', u''])
    if bsm_type == u'BSM_HEADER32':
      token = structure.parse_stream(file_object)
    elif bsm_type == u'BSM_HEADER64':
      token = structure.parse_stream(file_object)
    elif bsm_type == u'BSM_HEADER32_EX':
      token = structure.parse_stream(file_object)
    else:
      logging.warning(
          u'Token ID Header {0} not expected at position 0x{1:X}.'
          u'The parsing of the file cannot be continued'.format(
              token_id, file_object.tell()))
      # TODO: if it is a Mac OS X, search for the trailer magic value
      #       as a end of the entry can be a possibility to continue.
      return

    length = token.bsm_header.length
    event_type = u'{0} ({1})'.format(
        bsmtoken.BSM_AUDIT_EVENT.get(token.bsm_header.event_type, u'UNKNOWN'),
        token.bsm_header.event_type)
    timestamp = timelib.Timestamp.FromPosixTimeWithMicrosecond(
        token.timestamp, token.microsecond)

    # Read until we reach the end of the record.
    while file_object.tell() < (offset + length):
      # Check if it is a known token.
      try:
        token_id = self.BSM_TYPE.parse_stream(file_object)
      except (IOError, construct.FieldError):
        logging.warning(
            u'Unable to parse the Token ID at position: {0:d}'.format(
                file_object.tell()))
        return
      if not token_id in self.BSM_TYPE_LIST:
        pending = (offset + length) - file_object.tell()
        extra_tokens.extend(self.TryWithUntestedStructures(
            file_object, token_id, pending))
      else:
        token = self.BSM_TYPE_LIST[token_id][1].parse_stream(file_object)
        extra_tokens.append(self.FormatToken(token_id, token, file_object))

    if file_object.tell() > (offset + length):
      logging.warning(
          u'Token ID {0} not expected at position 0x{1:X}.'
          u'Jumping for the next entry.'.format(
              token_id, file_object.tell()))
      try:
        file_object.seek(
            (offset + length) - file_object.tell(), os.SEEK_CUR)
      except (IOError, construct.FieldError) as exception:
        logging.warning(
            u'Unable to jump to next entry with error: {0:s}'.format(exception))
        return

    # BSM can be in more than one OS: BSD, Solaris and Mac OS X.
    if parser_mediator.platform == u'MacOSX':
      # In Mac OS X the last two tokens are the return status and the trailer.
      if len(extra_tokens) >= 2:
        return_value = extra_tokens[-2:-1][0]
        if (return_value.startswith(u'[BSM_TOKEN_RETURN32') or
            return_value.startswith(u'[BSM_TOKEN_RETURN64')):
          _ = extra_tokens.pop(len(extra_tokens)-2)
        else:
          return_value = u'Return unknown'
      else:
        return_value = u'Return unknown'
      if extra_tokens:
        trailer = extra_tokens[-1]
        if trailer.startswith(u'[BSM_TOKEN_TRAILER'):
          _ = extra_tokens.pop(len(extra_tokens)-1)
        else:
          trailer = u'Trailer unknown'
      else:
        trailer = u'Trailer unknown'
      return MacBsmEvent(
          event_type, timestamp, u'. '.join(extra_tokens),
          return_value, trailer, offset)
    else:
      # Generic BSM format.
      if extra_tokens:
        trailer = extra_tokens[-1]
        if trailer.startswith(u'[BSM_TOKEN_TRAILER'):
          _ = extra_tokens.pop(len(extra_tokens)-1)
        else:
          trailer = u'Trailer unknown'
      else:
        trailer = u'Trailer unknown'
      return BsmEvent(
          event_type, timestamp, u'. '.join(extra_tokens), trailer, offset)