  def ParseChat(self, parser_mediator, row, query=None, **unused_kwargs):
    """Parses a chat message row.

    Args:
      parser_mediator: A parser mediator object (instance of ParserMediator).
      row: The row resulting from the query.
      query: Optional query string.
    """
    # Note that pysqlite does not accept a Unicode string in row['string'] and
    # will raise "IndexError: Index must be int or string".

    to_account = u''
    accounts = []
    participants = row['participants'].split(' ')
    for participant in participants:
      if participant != row['author']:
        accounts.append(participant)
    to_account = u', '.join(accounts)

    if not to_account:
      if row['dialog_partner']:
        to_account = row['dialog_partner']
      else:
        to_account = u'Unknown User'

    event_object = SkypeChatEvent(
        row['timestamp'], row['from_displayname'], row['author'], to_account,
        row['title'], row['body_xml'])
    parser_mediator.ProduceEvent(event_object, query=query)