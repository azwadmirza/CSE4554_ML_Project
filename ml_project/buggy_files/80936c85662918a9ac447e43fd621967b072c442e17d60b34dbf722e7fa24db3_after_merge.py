  def ParseIncomplete(self, match=None, **unused_kwargs):
    """Parse a partial line match and append to the body attribute.

    Args:
      match: optional regular expression match object (instance of SRE_Match).
             The default is None.
    """
    if not match:
      return

    try:
      self.attributes[u'body'] += match.group(0)
    except UnicodeDecodeError:
      # TODO: Support other encodings than UTF-8 here, read from the
      # knowledge base or parse from the file itself.
      self.attributes[u'body'] += u'{0:s}'.format(
          match.group(0).decode(u'utf-8', errors=u'ignore'))

    self.line_ready = True