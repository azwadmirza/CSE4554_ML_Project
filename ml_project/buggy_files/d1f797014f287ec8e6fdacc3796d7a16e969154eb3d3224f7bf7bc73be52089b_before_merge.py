  def SetTime(self, match=None, **unused_kwargs):
    """Set the time attribute.

    Args:
      match: The regular expression match object.
    """
    self.attributes['time'] = match.group(1)