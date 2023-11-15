  def __init__(self, datetime_time, timestamp_description, data_type=None):
    """Initializes an event.

    Args:
      datetime_time (datetime.datetime): datetime.
      timestamp_description (str): description of the usage of the timestamp
          value.
      data_type (Optional[str]): event data type. If the data type is not set
          it is derived from the DATA_TYPE class attribute.
    """
    timestamp = timelib.Timestamp.FromPythonDatetime(datetime_time)
    super(PythonDatetimeEvent, self).__init__(
        timestamp, timestamp_description, data_type=data_type)