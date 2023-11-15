  def ParseFileObject(self, parser_mediator, file_object, **unused_kwargs):
    """Parses a CSV text file-like object.

    Args:
      parser_mediator: A parser mediator object (instance of ParserMediator).
      file_object: A file-like object.

    Raises:
      UnableToParseFile: when the file cannot be parsed.
    """
    file_entry = parser_mediator.GetFileEntry()
    path_spec_printable = file_entry.path_spec.comparable.replace(u'\n', u';')

    text_file_object = text_file.TextFile(file_object)

    # If we specifically define a number of lines we should skip do that here.
    for _ in range(0, self.NUMBER_OF_HEADER_LINES):
      _ = text_file_object.readline()

    reader = csv.DictReader(
        text_file_object, fieldnames=self.COLUMNS,
        restkey=self.MAGIC_TEST_STRING, restval=self.MAGIC_TEST_STRING,
        delimiter=self.VALUE_SEPARATOR, quotechar=self.QUOTE_CHAR)

    try:
      row = reader.next()
    except (csv.Error, StopIteration):
      raise errors.UnableToParseFile(
          u'[{0:s}] Unable to parse CSV file: {1:s}.'.format(
              self.NAME, path_spec_printable))

    number_of_columns = len(self.COLUMNS)
    number_of_records = len(row)

    if number_of_records != number_of_columns:
      raise errors.UnableToParseFile((
          u'[{0:s}] Unable to parse CSV file: {1:s}. Wrong number of '
          u'records (expected: {2:d}, got: {3:d})').format(
              self.NAME, path_spec_printable, number_of_columns,
              number_of_records))

    for key, value in row.items():
      if key == self.MAGIC_TEST_STRING or value == self.MAGIC_TEST_STRING:
        raise errors.UnableToParseFile((
            u'[{0:s}] Unable to parse CSV file: {1:s}. Signature '
            u'mismatch.').format(self.NAME, path_spec_printable))

    if not self.VerifyRow(parser_mediator, row):
      raise errors.UnableToParseFile((
          u'[{0:s}] Unable to parse CSV file: {1:s}. Verification '
          u'failed.').format(self.NAME, path_spec_printable))

    self.ParseRow(parser_mediator, text_file_object.tell(), row)

    for row in reader:
      self.ParseRow(parser_mediator, text_file_object.tell(), row)