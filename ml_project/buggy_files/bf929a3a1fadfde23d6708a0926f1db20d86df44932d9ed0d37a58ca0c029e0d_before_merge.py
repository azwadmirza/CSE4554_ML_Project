  def __init__(self, row, timestamp, action_type, source, destination):
    """Actions related with sending files.

      Args:
        row:
          filepath: path from the file.
          filename: name of the file.
          filesize: size of the file.
        timestamp: when the action happens.
        action_type: GETSOLICITUDE, SENDSOLICITUDE, ACCEPTED, FINISHED.
        source: The account that sent the file.
        destination: The account that received the file.
    """
    # Note that pysqlite does not accept a Unicode string in row['string'] and
    # will raise "IndexError: Index must be int or string".

    super(SkypeTransferFileEvent, self).__init__(
        timestamp, u'File transfer from Skype', self.DATA_TYPE)

    self.offset = row['id']
    self.action_type = action_type
    self.source = source
    self.destination = destination
    self.transferred_filepath = row['filepath']
    self.transferred_filename = row['filename']

    try:
      self.transferred_filesize = int(row['filesize'])
    except ValueError:
      logging.debug(u'Unknown filesize {0:s}'.format(
          self.transferred_filename))
      self.transferred_filesize = 0