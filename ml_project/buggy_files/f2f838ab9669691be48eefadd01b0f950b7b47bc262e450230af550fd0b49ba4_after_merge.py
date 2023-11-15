  def GetTagging(self):
    """Retrieves the event tags.

    Yields:
      An event tag object (instance of EventTag).

    Raises:
      IOError: if the stream cannot be opened.
    """
    for stream_name in self._GetStreamNames():
      if not stream_name.startswith(u'plaso_tagging.'):
        continue

      if not self._HasStream(stream_name):
        raise IOError(u'No such stream: {0:s}'.format(stream_name))

      data_stream = _SerializedDataStream(
          self._zipfile, self._path, stream_name)

      event_tag = self._ReadEventTag(data_stream)
      while event_tag:
        yield event_tag
        event_tag = self._ReadEventTag(data_stream)