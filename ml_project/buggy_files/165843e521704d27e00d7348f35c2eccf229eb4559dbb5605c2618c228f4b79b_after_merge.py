  def SetYear(self, match=None, **unused_kwargs):
    """Parses the year.

       This is a callback function for the text parser (lexer) and is
       called by the corresponding lexer state.

    Args:
      match: optional regular expression match object (instance of SRE_Match).
             The default is None.
    """
    self.attributes[u'iyear'] = int(match.group(1))