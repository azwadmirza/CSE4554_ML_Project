  def __init__(self, java_time, timestamp_description, data_type=None):
    """Initializes an event object.

    Args:
      java_time (int): Java timestamp, which contains the number of
          milliseconds since January 1, 1970, 00:00:00 UTC.
      timestamp_description (str): description of the usage of the timestamp
          value.
      data_type (Optional[str]): event data type. If the data type is not set
          it is derived from the DATA_TYPE class attribute.
    """
    timestamp = timelib.Timestamp.FromJavaTime(java_time)
    super(JavaTimeEvent, self).__init__(
        timestamp, timestamp_description, data_type=data_type)