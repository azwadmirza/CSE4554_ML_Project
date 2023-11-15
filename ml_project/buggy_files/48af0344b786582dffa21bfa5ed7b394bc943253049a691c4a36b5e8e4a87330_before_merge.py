  def __init__(self, systemtime, timestamp_description, data_type=None):
    """Initializes an event object.

    Args:
      systemtime (bytes): 128-bit SYSTEMTIME timestamp value.
      timestamp_description (str): description of the usage of the timestamp
          value.
      data_type (Optional[str]): event data type. If the data type is not set
          it is derived from the DATA_TYPE class attribute.
    """
    timestamp = timelib.Timestamp.FromSystemtime(systemtime)
    super(SystemtimeEvent, self).__init__(
        timestamp, timestamp_description, data_type=data_type)