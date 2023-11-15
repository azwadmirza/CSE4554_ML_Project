  def __init__(
      self, posix_time, from_displayname, author, to_account, title, body_xml):
    """Build a Skype Event from a single row.

    Args:
      posix_time: the POSIX time value, which contains the number of seconds
                  since January 1, 1970 00:00:00 UTC.
      from_displayname: a string containing the from display name.
      author: a string containing the author.
      to_account: a string containing the accounts (excluding the
                  author) of the conversation.
      title: a string containing the title.
      body_xml: a string containing the body XML.
    """
    super(SkypeChatEvent, self).__init__(posix_time, u'Chat from Skype')
    self.from_account = u'{0:s} <{1:s}>'.format(from_displayname, author)
    self.text = body_xml
    self.title = title
    self.to_account = to_account