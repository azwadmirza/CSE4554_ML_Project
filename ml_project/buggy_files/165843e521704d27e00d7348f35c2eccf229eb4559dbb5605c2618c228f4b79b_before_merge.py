  def SetYear(self, match=None, **unused_kwargs):
    """Parses the year.

       This is a callback function for the text parser (lexer) and is
       called by the corresponding lexer state.

    Args:
      match: The regular expression match object.
    """
    self.attributes['iyear'] = int(match.group(1))