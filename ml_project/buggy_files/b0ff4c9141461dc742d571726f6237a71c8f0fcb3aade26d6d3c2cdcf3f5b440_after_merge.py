  def _GetSerializedEventObjectStream(self, stream_number):
    """Retrieves the serialized event object stream.

    Args:
      stream_number: an integer containing the number of the stream.

    Returns:
      A serialized data stream object (instance of _SerializedDataStream).

    Raises:
      IOError: if the stream cannot be opened.
    """
    data_stream = self._event_object_streams.get(stream_number, None)
    if not data_stream:
      stream_name = u'plaso_proto.{0:06d}'.format(stream_number)
      if not self._HasStream(stream_name):
        raise IOError(u'No such stream: {0:s}'.format(stream_name))

      data_stream = _SerializedDataStream(
          self._zipfile, self._path, stream_name)
      self._event_object_streams[stream_number] = data_stream

    return data_stream