  def VerifyRow(self, parser_mediator, row):
    """Verify that this is a McAfee AV Access Protection Log file.

    Args:
      parser_mediator: A parser mediator object (instance of ParserMediator).
      row: A single row from the CSV file.

    Returns:
      True if this is the correct parser, False otherwise.
    """
    if len(row) != 8:
      return False

    # This file can have a UTF-8 byte-order-marker at the beginning of
    # the first row.
    # TODO: Find out all the code pages this can have.  Asked McAfee 10/31.
    if row[u'date'][0:3] == b'\xef\xbb\xbf':
      row[u'date'] = row[u'date'][3:]
      self.encoding = u'utf-8'

    # Check the date format!
    # If it doesn't pass, then this isn't a McAfee AV Access Protection Log
    timestamp = self._GetTimestamp(parser_mediator, row[u'date'], row[u'time'])
    if timestamp is None:
      return False

    # Use the presence of these strings as a backup or in case of partial file.
    if (not u'Access Protection' in row[u'status'] and
        not u'Would be blocked' in row[u'status']):
      return False

    return True