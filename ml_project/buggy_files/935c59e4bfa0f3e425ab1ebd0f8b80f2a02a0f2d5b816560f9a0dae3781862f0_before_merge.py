  def ParseFileObject(self, parser_mediator, file_object, **kwargs):
    """Parses a text file-like object using a lexer.

    Args:
      parser_mediator: A parser mediator object (instance of ParserMediator).
      file_object: A file-like object.

    Raises:
      UnableToParseFile: when the file cannot be parsed.
    """
    file_entry = parser_mediator.GetFileEntry()
    path_spec_printable = u'{0:s}:{1:s}'.format(
        file_entry.path_spec.type_indicator, file_entry.name)

    self.file_entry = file_entry
    # TODO: this is necessary since we inherit from lexer.SelfFeederMixIn.
    self.file_object = file_object

    # Start by checking, is this a text file or not? Before we proceed
    # any further.
    file_object.seek(0, os.SEEK_SET)
    if not utils.IsText(file_object.read(40)):
      raise errors.UnableToParseFile(u'Not a text file, unable to proceed.')

    file_object.seek(0, os.SEEK_SET)

    error_count = 0
    file_verified = False
    # We need to clear out few values in the Lexer before continuing.
    # There might be some leftovers from previous run.
    self.error = 0
    self.buffer = ''

    while True:
      _ = self.NextToken()

      if self.state == 'INITIAL':
        self.entry_offset = getattr(self, 'next_entry_offset', 0)
        self.next_entry_offset = file_object.tell() - len(self.buffer)

      if not file_verified and self.error >= self.MAX_LINES * 2:
        logging.debug(
            u'Lexer error count: {0:d} and current state {1:s}'.format(
                self.error, self.state))
        raise errors.UnableToParseFile(
            u'[{0:s}] unsupported file: {1:s}.'.format(
                self.NAME, path_spec_printable))

      if self.line_ready:
        try:
          self.ParseLine(parser_mediator)
          file_verified = True

        except errors.TimestampNotCorrectlyFormed as exception:
          error_count += 1
          if file_verified:
            logging.debug(
                u'[{0:s} VERIFIED] Error count: {1:d} and ERROR: {2:d}'.format(
                    path_spec_printable, error_count, self.error))
            logging.warning(
                u'[{0:s}] Unable to parse timestamp with error: {1:s}'.format(
                    self.NAME, exception))

          else:
            logging.debug((
                u'[{0:s} EVALUATING] Error count: {1:d} and ERROR: '
                u'{2:d})').format(path_spec_printable, error_count, self.error))

            if error_count >= self.MAX_LINES:
              raise errors.UnableToParseFile(
                  u'[{0:s}] unsupported file: {1:s}.'.format(
                      self.NAME, path_spec_printable))

        finally:
          self.ClearValues()

      if self.Empty():
        # Try to fill the buffer to prevent the parser from ending prematurely.
        self.Feed()

      if self.Empty():
        break

    if not file_verified:
      raise errors.UnableToParseFile(
          u'[{0:s}] unable to parser file: {1:s}.'.format(
              self.NAME, path_spec_printable))

    file_offset = file_object.get_offset()
    if file_offset < file_object.get_size():
      parser_mediator.ProduceParseError((
          u'{0:s} prematurely terminated parsing: {1:s} at offset: '
          u'0x{2:08x}.').format(
              self.NAME, path_spec_printable, file_offset))