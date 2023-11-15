  def ParseString(self, match=None, **unused_kwargs):
    """Return a string with combined values from the lexer.

    Args:
      match: The regular expression match object.

    Returns:
      A string that combines the values that are so far
      saved from the lexer.
    """
    try:
      self.attributes['body'] += match.group(1).strip('\n')
    except IndexError:
      self.attributes['body'] += match.group(0).strip('\n')