  def ParseString(self, match=None, **unused_kwargs):
    """Return a string with combined values from the lexer.

    Args:
      match: optional regular expression match object (instance of SRE_Match).
             The default is None.

    Returns:
      A string that combines the values that are so far
      saved from the lexer.
    """
    try:
      self.attributes[u'body'] += match.group(1).strip('\n')
    except IndexError:
      self.attributes[u'body'] += match.group(0).strip('\n')