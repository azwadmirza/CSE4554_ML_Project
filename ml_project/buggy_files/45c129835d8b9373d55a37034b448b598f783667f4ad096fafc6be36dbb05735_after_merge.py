  def _GetEventDataHexDump(
      self, event_object, before=0, maximum_number_of_lines=20):
    """Returns a hexadecimal representation of the event data.

     This function creates a hexadecimal string representation based on
     the event data described by the event object.

    Args:
      event_object: The event object (instance of EventObject).
      before: Optional number of bytes to include in the output before
              the event. The default is none.
      maximum_number_of_lines: Optional maximum number of lines to include
                               in the output. The default is 20.

    Returns:
      A string that contains the hexadecimal representation of the event data.
    """
    if not event_object:
      return u'Missing event object.'

    if not hasattr(event_object, u'pathspec'):
      return u'Event object has no path specification.'

    try:
      file_entry = resolver.Resolver.OpenFileEntry(event_object.pathspec)
    except IOError as exception:
      return u'Unable to open file with error: {0:s}'.format(exception)

    offset = getattr(event_object, u'offset', 0)
    if offset - before > 0:
      offset -= before

    file_object = file_entry.GetFileObject()
    file_object.seek(offset, os.SEEK_SET)
    data_size = maximum_number_of_lines * 16
    data = file_object.read(data_size)
    file_object.close()

    return hexdump.Hexdump.FormatData(data)