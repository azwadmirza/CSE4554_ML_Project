  def __init__(self, delphi_time, timestamp_description, data_type=None):
    """Initializes an event.

    Args:
      delphi_time (int): Delphi time value.
      timestamp_description (str): description of the usage of the timestamp
          value.
      data_type (Optional[str]): event data type. If the data type is not set
          it is derived from the DATA_TYPE class attribute.
    """
    timestamp = timelib.Timestamp.FromDelphiTime(delphi_time)
    super(DelphiTimeEvent, self).__init__(
        timestamp, timestamp_description, data_type=data_type)