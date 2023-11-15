  def _WritePreprocessObject(self, pre_obj):
    """Writes a preprocess object to the storage file.

    Args:
      pre_obj: the preprocess object (instance of PreprocessObject).

    Raises:
      IOError: if the stream cannot be opened.
    """
    existing_stream_data = self._ReadStream(u'information.dump')

    # Store information about store range for this particular
    # preprocessing object. This will determine which stores
    # this information is applicable for.
    if self._serializers_profiler:
      self._serializers_profiler.StartTiming(u'pre_obj')

    pre_obj_data = self._pre_obj_serializer.WriteSerialized(pre_obj)

    if self._serializers_profiler:
      self._serializers_profiler.StopTiming(u'pre_obj')

    # TODO: use _SerializedDataStream.
    pre_obj_data_size = construct.ULInt32(u'size').build(len(pre_obj_data))
    stream_data = b''.join([
        existing_stream_data, pre_obj_data_size, pre_obj_data])

    self._WriteStream(u'information.dump', stream_data)