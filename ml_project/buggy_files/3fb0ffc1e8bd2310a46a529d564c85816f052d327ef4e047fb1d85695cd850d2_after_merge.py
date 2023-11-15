  def _ReadLine(
      self, parser_mediator, file_entry, text_file_object, max_len=0,
      quiet=False, depth=0):
    """Read a single line from a text file and return it back.

    Args:
      parser_mediator: a parser mediator object (instance of ParserMediator).
      file_entry: a file entry object (instance of dfvfs.FileEntry).
      text_file_object: a text file object (instance of dfvfs.TextFile).
      max_len: if defined determines the maximum number of bytes a single line
               can take.
      quiet: if True then a decode warning is not displayed.
      depth: a threshold of how many newlines we can encounter before bailing
             out.

    Returns:
      A single line read from the file-like object, or the maximum number of
      characters (if max_len defined and line longer than the defined size).
    """
    if max_len:
      line = text_file_object.readline(max_len)
    else:
      line = text_file_object.readline()

    if not line:
      return

    # If line is empty, skip it and go on.
    if line == '\n' or line == '\r\n':
      # Max 40 new lines in a row before we bail out.
      if depth == 40:
        return ''

      return self._ReadLine(
          parser_mediator, file_entry, text_file_object, max_len=max_len,
          depth=depth + 1)

    if not self.encoding:
      return line.strip()

    try:
      decoded_line = line.decode(self.encoding)
      return decoded_line.strip()
    except UnicodeDecodeError:
      if not quiet:
        logging.warning((
            u'Unable to decode line [{0:s}...] with encoding: {1:s} in '
            u'file: {2:s}').format(
                repr(line[1:30]), self.encoding,
                parser_mediator.GetDisplayName(file_entry)))
      return line.strip()