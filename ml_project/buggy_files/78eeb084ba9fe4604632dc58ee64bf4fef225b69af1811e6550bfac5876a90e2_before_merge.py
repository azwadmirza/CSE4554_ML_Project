  def ReadPair(self, parser_mediator, file_object):
    """Reads an attribute name and value pair from a CUPS IPP event.

    Args:
      parser_mediator: A parser mediator object (instance of ParserMediator).
      file_object: a file-like object that points to a file.

    Returns:
      A list of name and value. If name and value cannot be read both are
      set to None.
    """
    # Pair = Type ID + Name + Value.
    try:
      # Can be:
      #   Group ID + IDtag = Group ID (1byte) + Tag ID (1byte) + '0x00'.
      #   IDtag = Tag ID (1byte) + '0x00'.
      type_id = self.INTEGER_8.parse_stream(file_object)
      if type_id == self.GROUP_END:
        return None, None

      elif type_id in self.GROUP_LIST:
        # If it is a group ID we must read the next byte that contains
        # the first TagID.
        type_id = self.INTEGER_8.parse_stream(file_object)

      # 0x00 separator character.
      _ = self.INTEGER_8.parse_stream(file_object)

    except (IOError, construct.FieldError):
      logging.warning(
          u'[{0:s}] Unsupported identifier in file: {1:s}.'.format(
              self.NAME, parser_mediator.GetDisplayName()))
      return None, None

    # Name = Length name + name + 0x00
    try:
      name = self.PAIR_NAME.parse_stream(file_object).text
    except (IOError, construct.FieldError):
      logging.warning(
          u'[{0:s}] Unsupported name in file: {1:s}.'.format(
              self.NAME, parser_mediator.GetDisplayName()))
      return None, None

    # Value: can be integer, boolean or text select by Type ID.
    try:
      if type_id in [
          self.TYPE_GENERAL_INTEGER, self.TYPE_INTEGER, self.TYPE_ENUMERATION]:
        value = self.INTEGER.parse_stream(file_object).integer

      elif type_id == self.TYPE_BOOL:
        value = bool(self.BOOLEAN.parse_stream(file_object).integer)

      elif type_id == self.TYPE_DATETIME:
        datetime = self.DATETIME.parse_stream(file_object)
        value = timelib.Timestamp.FromRFC2579Datetime(
            datetime.year, datetime.month, datetime.day, datetime.hour,
            datetime.minutes, datetime.seconds, datetime.deciseconds,
            datetime.direction_from_utc, datetime.hours_from_utc,
            datetime.minutes_from_utc)

      else:
        value = self.TEXT.parse_stream(file_object)

    except (IOError, UnicodeDecodeError, construct.FieldError):
      logging.warning(
          u'[{0:s}] Unsupported value in file: {1:s}.'.format(
              self.NAME, parser_mediator.GetDisplayName()))
      return None, None

    return name, value