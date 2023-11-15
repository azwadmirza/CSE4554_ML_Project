  def Parse(self, parser_context, file_entry, parser_chain=None):
    """Parse a text file using a pyparsing definition.

    Args:
      parser_context: A parser context object (instance of ParserContext).
      file_entry: A file entry object (instance of dfvfs.FileEntry).
      parser_chain: Optional string containing the parsing chain up to this
                    point. The default is None.

    Raises:
      UnableToParseFile: if the line structures are missing.
    """
    if not self.LINE_STRUCTURES:
      raise errors.UnableToParseFile(u'Missing line structures.')

    self._text_reader.Reset()

    file_object = file_entry.GetFileObject()
    file_object.seek(0, os.SEEK_SET)

    try:
      self._text_reader.ReadLines(file_object)
    except UnicodeDecodeError as exception:
      raise errors.UnableToParseFile(
          u'Not a text file, with error: {0:s}'.format(exception))

    if not utils.IsText(self._text_reader.lines):
      raise errors.UnableToParseFile(u'Not a text file, unable to proceed.')

    if not self.VerifyStructure(parser_context, self._text_reader.lines):
      raise errors.UnableToParseFile(u'Wrong file structure.')

    # Add ourselves to the parser chain, which will be used in all subsequent
    # event creation in this parser.
    parser_chain = self._BuildParserChain(parser_chain)

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
        parsed_event = self.ParseRecord(parser_context, key, tokens)
        if parsed_event:
          # TODO: need a reliable way to handle this.
          # parsed_event.offset = self._text_reader.line_offset
          parser_context.ProduceEvent(
              parsed_event, parser_chain=parser_chain, file_entry=file_entry)

        self._text_reader.SkipAhead(file_object, end)

      else:
        odd_line = self._text_reader.ReadLine(file_object)
        if odd_line:
          logging.warning(
              u'Unable to parse log line: {0:s}'.format(repr(odd_line)))

      try:
        self._text_reader.ReadLines(file_object)
      except UnicodeDecodeError as exception:
        logging.error(
            u'[{0:s}] Unable to read lines from file: {1:s} with error: '
            u'{2:s}'.format(
                parser_chain,
                file_entry.path_spec.comparable.replace(u'\n', u';'),
                exception))