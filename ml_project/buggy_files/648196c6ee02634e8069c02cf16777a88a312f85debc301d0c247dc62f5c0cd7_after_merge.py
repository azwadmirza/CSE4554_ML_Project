  def ParseSMS(self, parser_mediator, row, query=None, **unused_kwargs):
    """Parse SMS.

    Args:
      parser_mediator: A parser mediator object (instance of ParserMediator).
      row: The row resulting from the query.
      query: Optional query string.
    """
    # Note that pysqlite does not accept a Unicode string in row['string'] and
    # will raise "IndexError: Index must be int or string".

    phone_number = row['dstnum_sms']
    if phone_number:
      phone_number = phone_number.replace(u' ', u'')

    event_object = SkypeSMSEvent(row['time_sms'], phone_number, row['msg_sms'])
    parser_mediator.ProduceEvent(event_object, query=query)