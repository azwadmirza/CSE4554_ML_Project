  def ParseFileObject(self, parser_mediator, file_object, **kwargs):
    """Parses a text file-like object using a pyparsing definition.

    Args:
      parser_mediator: A parser mediator object (instance of ParserMediator).
      file_object: A file-like object.

    Raises:
      UnableToParseFile: when the file cannot be parsed.
    """
    if not self.LINE_STRUCTURES:
      raise errors.UnableToParseFile(u'Missing line structures.')

    self._text_reader.Reset()

    try:
      self._text_reader.ReadLines(file_object)
    except UnicodeDecodeError as exception:
      raise errors.UnableToParseFile(
          u'Not a text file, with error: {0:s}'.format(exception))

    if not utils.IsText(self._text_reader.lines):
      raise errors.UnableToParseFile(u'Not a text file, unable to proceed.')

    if not self.VerifyStructure(parser_mediator, self._text_reader.lines):
      raise errors.UnableToParseFile(u'Wrong file structure.')

    # Read every line in the text file.
    while self._text_reader.lines:
      # Initialize pyparsing objects.
      tokens = None
      start = 0
      end = 0

      key = None

      # Try to parse the line using all the line structures.
      for key, structure in self.LINE_STRUCTURES:
        try:
          parsed_structure = next(
              structure.scanString(self._text_reader.lines, maxMatches=1), None)
        except pyparsing.ParseException:
          continue

        if not parsed_structure:
          continue

        tokens, start, end = parsed_structure

        # Only want to parse the structure if it starts
        # at the beginning of the buffer.
        if start == 0:
          break

      if tokens and start == 0:
        parsed_event = self.ParseRecord(parser_mediator, key, tokens)
        if parsed_event:
          # TODO: need a reliable way to handle this.
          # parsed_event.offset = self._text_reader.line_offset
          parser_mediator.ProduceEvent(parsed_event)

        self._text_reader.SkipAhead(file_object, end)

      else:
        odd_line = self._text_reader.ReadLine(file_object)
        if odd_line:
          logging.warning(
              u'Unable to parse log line: {0:s}'.format(repr(odd_line)))

      try:
        self._text_reader.ReadLines(file_object)
      except UnicodeDecodeError as exception:
        parser_mediator.ProduceParseError(
            u'Unable to read lines from file with error: {0:s}'.format(
                exception))