  def __init__(
      self, posix_time, identifier, action_type, source, destination, filename,
      file_path, file_size):
    """Actions related with sending files.

    Args:
      posix_time: the POSIX time value, which contains the number of seconds
                  since January 1, 1970 00:00:00 UTC.
      identifier: an integer containing the row identifier.
      action_type: a string containing the action type e.g. GETSOLICITUDE,
                   SENDSOLICITUDE, ACCEPTED, FINISHED.
      source: a string containing the account that sent the file.
      destination: a string containing the account that received the file.
      filename: a string containing the name of the file transferred.
      file_path: a string containing the path of the file transferred.
      file_size: an integer containing the size of the file transferred.
    """
    # Note that pysqlite does not accept a Unicode string in row['string'] and
    # will raise "IndexError: Index must be int or string".

    super(SkypeTransferFileEvent, self).__init__(
        posix_time, u'File transfer from Skype')
    self.action_type = action_type
    self.destination = destination
    self.offset = identifier
    self.source = source
    self.transferred_filename = filename
    self.transferred_filepath = file_path
    self.transferred_filesize = file_size