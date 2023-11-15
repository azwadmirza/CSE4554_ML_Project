  def __init__(self, uuid, timestamp_description):
    """Initializes an event object.

    Args:
      uuid (uuid.UUID): UUID object.
      timestamp_description (str): description of the usage of the timestamp
          value.

    Raises:
      ValueError: if the UUID version is not supported.
    """
    if uuid.version != 1:
      raise ValueError(u'Unsupported UUID version.')

    timestamp = timelib.Timestamp.FromUUIDTime(uuid.time)
    mac_address = u'{0:s}:{1:s}:{2:s}:{3:s}:{4:s}:{5:s}'.format(
        uuid.hex[20:22], uuid.hex[22:24], uuid.hex[24:26], uuid.hex[26:28],
        uuid.hex[28:30], uuid.hex[30:32])
    super(UUIDTimeEvent, self).__init__(timestamp, timestamp_description)

    self.mac_address = mac_address
    self.uuid = u'{0!s}'.format(uuid)