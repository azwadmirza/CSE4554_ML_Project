  def VerifyFile(self, file_object):
    """Check if the file is a PLSRecall.dat file.

    Args:
      file_object: file that we want to check.

    Returns:
      True if this is a valid PLSRecall.dat file, otherwise False.
    """
    file_object.seek(0, os.SEEK_SET)

    # The file consists of PL/SQL structures that are equal
    # size (4125 bytes) TRecallRecord records. It should be
    # noted that the query value is free form.
    try:
      structure = self.PLS_STRUCT.parse_stream(file_object)
    except (IOError, construct.FieldError):
      return False

    # Verify few entries inside the structure.
    try:
      timestamp = timelib.Timestamp.FromDelphiTime(structure.TimeStamp)
    except ValueError:
      return False

    if timestamp <= 0:
      return False

    # TODO: Add other verification checks here. For instance make sure
    # that the query actually looks like a SQL query. This structure produces a
    # lot of false positives and thus we need to add additional verification to
    # make sure we are not parsing non-PLSRecall files.
    # Another check might be to make sure the username looks legitimate, or the
    # sequence number, or the database name.
    # For now we just check if all three fields pass our "is this a text" test.
    if not utils.IsText(structure.Username):
      return False
    if not utils.IsText(structure.Query):
      return False
    if not utils.IsText(structure.Database):
      return False

    return True