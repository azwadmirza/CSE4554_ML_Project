  def ParseFileObject(self, parser_mediator, file_object, **kwargs):
    """Parses a text file-like object using a pyparsing definition.

    Args:
      parser_mediator: a parser mediator object (instance of ParserMediator).
      file_object: a file-like object.

    Raises:
      UnableToParseFile: when the file cannot be parsed.
    """
    file_entry = parser_mediator.GetFileEntry()

    # TODO: find a more elegant way for this; currently the mac_wifi and
    # syslog parser seem to rely on this member.
    self.file_entry = file_entry

    # TODO: self._line_structures is a work-around and this needs
    # a structural fix.
    if not self._line_structures:
      raise errors.UnableToParseFile(
          u'Line structure undeclared, unable to proceed.')

    text_file_object = text_file.TextFile(file_object)

    line = self._ReadLine(
        parser_mediator, file_entry, text_file_object,
        max_len=self.MAX_LINE_LENGTH, quiet=True)
    if not line:
      raise errors.UnableToParseFile(u'Not a text file.')

    if len(line) == self.MAX_LINE_LENGTH or len(
        line) == self.MAX_LINE_LENGTH - 1:
      logging.debug((
          u'Trying to read a line and reached the maximum allowed length of '
          u'{0:d}. The last few bytes of the line are: {1:s} [parser '
          u'{2:s}]').format(
              self.MAX_LINE_LENGTH, repr(line[-10:]), self.NAME))

    if not utils.IsText(line):
      raise errors.UnableToParseFile(u'Not a text file, unable to proceed.')

    if not self.VerifyStructure(parser_mediator, line):
      raise errors.UnableToParseFile(u'Wrong file structure.')

    # Set the offset to the beginning of the file.
    self._current_offset = 0
    # Read every line in the text file.
    while line:
      parsed_structure = None
      use_key = None
      # Try to parse the line using all the line structures.
      for key, structure in self.LINE_STRUCTURES:
        try:
          parsed_structure = structure.parseString(line)
        except pyparsing.ParseException:
          pass
        if parsed_structure:
          use_key = key
          break

      if parsed_structure:
        parsed_event = self.ParseRecord(
            parser_mediator, use_key, parsed_structure)
        if parsed_event:
          parsed_event.offset = self._current_offset
          parser_mediator.ProduceEvent(parsed_event)
      else:
        logging.warning(u'Unable to parse log line: {0:s}'.format(line))

      self._current_offset = text_file_object.get_offset()
      line = self._ReadLine(parser_mediator, file_entry, text_file_object)