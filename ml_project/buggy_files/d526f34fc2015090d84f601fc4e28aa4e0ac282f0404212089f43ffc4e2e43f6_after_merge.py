  def __init__(
      self, posix_time, timestamp_description, data_type=None, micro_seconds=0):
    """Initializes an event.

    Args:
      posix_time (int): POSIX time value, which contains the number of seconds
          since January 1, 1970 00:00:00 UTC.
      timestamp_description (str): description of the usage of the timestamp
          value.
      data_type (Optional[str]): event data type. If the data type is not set
          it is derived from the DATA_TYPE class attribute.
      micro_seconds: optional number of micro seconds.
    """
    if micro_seconds:
      timestamp = timelib.Timestamp.FromPosixTimeWithMicrosecond(
          posix_time, micro_seconds)
    else:
      timestamp = timelib.Timestamp.FromPosixTime(posix_time)

    super(PosixTimeEvent, self).__init__(
        timestamp, timestamp_description, data_type=data_type)