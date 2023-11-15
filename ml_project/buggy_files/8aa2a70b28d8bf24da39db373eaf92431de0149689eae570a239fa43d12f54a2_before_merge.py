  def _BuildTagIndex(self):
    """Builds the tag index that contains the offsets for each tag.

    Raises:
      IOError: if the stream cannot be opened.
    """
    self._event_tag_index = {}

    for stream_name in self._GetStreamNames():
      if not stream_name.startswith(u'plaso_tag_index.'):
        continue

      file_object = self._OpenStream(stream_name)
      if file_object is None:
        raise IOError(u'Unable to open stream: {0:s}'.format(stream_name))

      _, _, store_number = stream_name.rpartition(u'.')
      try:
        store_number = int(store_number, 10)
      except ValueError as exception:
        raise IOError((
            u'Unable to determine store number of stream: {0:s} '
            u'with error: {1:s}').format(stream_name, exception))

      while True:
        tag_index_value = _EventTagIndexValue.Read(file_object, store_number)
        if tag_index_value is None:
          break

        self._event_tag_index[tag_index_value.identifier] = tag_index_value