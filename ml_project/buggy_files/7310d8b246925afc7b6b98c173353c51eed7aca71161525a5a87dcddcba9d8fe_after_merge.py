  def SetMonth(self, match=None, **unused_kwargs):
    """Parses the month.

       This is a callback function for the text parser (lexer) and is
       called by the corresponding lexer state.

    Args:
      match: optional regular expression match object (instance of SRE_Match).
             The default is None.
    """
    self.attributes[u'imonth'] = int(
        timelib.MONTH_DICT.get(match.group(1).lower(), 1))