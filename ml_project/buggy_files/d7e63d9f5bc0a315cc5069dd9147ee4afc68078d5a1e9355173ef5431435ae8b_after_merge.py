  def __init__(self, fat_date_time, timestamp_description, data_type=None):
    """Initializes an event.

    Args:
      fat_date_time (int): FAT date time value.
      timestamp_description (str): description of the usage of the timestamp
          value.
      data_type (Optional[str]): event data type. If the data type is not set
          it is derived from the DATA_TYPE class attribute.
    """
    timestamp = timelib.Timestamp.FromFatDateTime(fat_date_time)
    super(FatDateTimeEvent, self).__init__(
        timestamp, timestamp_description, data_type=data_type)