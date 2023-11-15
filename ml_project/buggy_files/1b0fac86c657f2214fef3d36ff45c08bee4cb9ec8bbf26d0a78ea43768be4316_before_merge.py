  def __init__(self, row, to_account):
    """Build a Skype Event from a single row.

    Args:
      row: A row object (instance of sqlite3.Row) that contains the
           extracted data from a single row in the database.
      to_account: A string containing the accounts (excluding the
                  author) of the conversation.
    """
    # Note that pysqlite does not accept a Unicode string in row['string'] and
    # will raise "IndexError: Index must be int or string".

    super(SkypeChatEvent, self).__init__(
        row['timestamp'], u'Chat from Skype', self.DATA_TYPE)

    self.title = row['title']
    self.text = row['body_xml']
    self.from_account = u'{0:s} <{1:s}>'.format(
        row['from_displayname'], row['author'])
    self.to_account = to_account