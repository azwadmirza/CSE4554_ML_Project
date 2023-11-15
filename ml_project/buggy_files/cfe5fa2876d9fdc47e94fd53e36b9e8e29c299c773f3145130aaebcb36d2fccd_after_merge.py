  def VerifyRow(self, unused_parser_mediator, unused_row):
    """Return a bool indicating whether or not this is the correct parser.

    Args:
      parser_mediator: a parser mediator object (instance of ParserMediator).
      row: a single row from the CSV file. Strings in this dict are binary
           strings, to aid in file verification.

    Returns:
      True if this is the correct parser, False otherwise.
    """
    pass