  def __init__(self, local_zone=True):
    """Constructor for the SlowLexicalTextParser.

    Args:
      local_zone: a boolean value that determines if the entries
                  in the log file are stored in the local time
                  zone of the computer that stored it or in a fixed
                  timezone, like UTC.
    """
    # TODO: remove the multiple inheritance.
    lexer.SelfFeederMixIn.__init__(self)
    interface.SingleFileBaseParser.__init__(self)
    self.line_ready = False
    self.attributes = {
        u'body': u'',
        u'iyear': 0,
        u'imonth': 0,
        u'iday': 0,
        u'time': u'',
        u'hostname': u'',
        u'username': u'',
    }
    self.local_zone = local_zone
    self.file_entry = None