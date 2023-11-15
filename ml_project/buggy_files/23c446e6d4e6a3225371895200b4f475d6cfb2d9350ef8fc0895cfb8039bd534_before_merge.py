  def __init__(self, local_zone=True):
    """Constructor for the SlowLexicalTextParser.

    Args:
      local_zone: A boolean value that determines if the entries
                  in the log file are stored in the local time
                  zone of the computer that stored it or in a fixed
                  timezone, like UTC.
    """
    # TODO: remove the multiple inheritance.
    lexer.SelfFeederMixIn.__init__(self)
    interface.SingleFileBaseParser.__init__(self)
    self.line_ready = False
    self.attributes = {
        'body': '',
        'iyear': 0,
        'imonth': 0,
        'iday': 0,
        'time': '',
        'hostname': '',
        'username': '',
    }
    self.local_zone = local_zone
    self.file_entry = None