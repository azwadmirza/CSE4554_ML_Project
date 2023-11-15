  def SetTime(self, match=None, **unused_kwargs):
    """Set the time attribute.

    Args:
      match: optional regular expression match object (instance of SRE_Match).
             The default is None.
    """
    self.attributes[u'time'] = match.group(1)