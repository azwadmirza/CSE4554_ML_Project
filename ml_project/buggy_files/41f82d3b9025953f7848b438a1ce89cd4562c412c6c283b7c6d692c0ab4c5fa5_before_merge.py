  def SetDay(self, match=None, **unused_kwargs):
    """Parses the day of the month.

       This is a callback function for the text parser (lexer) and is
       called by the corresponding lexer state.

    Args:
      match: The regular expression match object.
    """
    self.attributes['iday'] = int(match.group(1))