  def ParseIncomplete(self, match=None, **unused_kwargs):
    """Indication that we've got a partial line to match against.

    Args:
      match: The regular expression match object.
    """
    self.attributes['body'] += match.group(0)
    self.line_ready = True