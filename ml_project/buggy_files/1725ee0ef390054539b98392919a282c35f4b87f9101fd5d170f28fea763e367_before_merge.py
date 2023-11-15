  def StoreTagging(self, tags):
    """Store tag information into the storage file.

    Each EventObject can be tagged either manually or automatically
    to make analysis simpler, by providing more context to certain
    events or to highlight events for later viewing.

    The object passed in needs to be a list (or otherwise an iterator)
    that contains EventTag objects (event.EventTag).

    Args:
      A list or an object providing an iterator that contains
      EventTag objects.

    Raises:
      IOError: if the stream cannot be opened.
    """
    if not self._pre_obj:
      self._pre_obj = event.PreprocessObject()

    if not hasattr(self._pre_obj, u'collection_information'):
      self._pre_obj.collection_information = {}

    self._pre_obj.collection_information[u'Action'] = u'Adding tags to storage.'
    self._pre_obj.collection_information[u'time_of_run'] = (
        timelib.Timestamp.GetNow())
    if not hasattr(self._pre_obj, u'counter'):
      self._pre_obj.counter = collections.Counter()

    tag_number = 1
    for name in self._GetStreamNames():
      if not name.startswith(u'plaso_tagging.'):
        continue

      _, _, number_string = name.partition(u'.')
      try:
        number = int(number_string, 10)
      except ValueError:
        continue

      if number >= tag_number:
        tag_number = number + 1
      if self._event_tag_index is None:
        self._BuildTagIndex()

    serialized_event_tags = []
    for tag in tags:
      self._pre_obj.counter[u'Total Tags'] += 1
      if hasattr(tag, u'tags'):
        for tag_entry in tag.tags:
          self._pre_obj.counter[tag_entry] += 1

      if self._event_tag_index is not None:
        tag_index_value = self._event_tag_index.get(tag.string_key, None)
      else:
        tag_index_value = None

      # This particular event has already been tagged on a previous occasion,
      # we need to make sure we are appending to that particular tag.
      if tag_index_value is not None:
        stream_name = u'plaso_tagging.{0:06d}'.format(
            tag_index_value.store_number)

        if not self._HasStream(stream_name):
          raise IOError(u'No such stream: {0:s}'.format(stream_name))

        data_stream = _SerializedDataStream(self._zipfile, stream_name)
        # TODO: replace 0 by the actual event tag entry index.
        # This is for code consistency rather then a functional purpose.
        data_stream.SeekEntryAtOffset(0, tag_index_value.offset)

        # TODO: if old_tag is cached make sure to update cache after write.
        old_tag = self._ReadEventTag(data_stream)
        if not old_tag:
          continue

        # TODO: move the append functionality into EventTag.
        # Maybe name the function extend or update?
        if hasattr(old_tag, u'tags'):
          tag.tags.extend(old_tag.tags)

        if hasattr(old_tag, u'comment'):
          if hasattr(tag, u'comment'):
            tag.comment += old_tag.comment
          else:
            tag.comment = old_tag.comment

        if hasattr(old_tag, u'color') and not hasattr(tag, u'color'):
          tag.color = old_tag.color

      if self._serializers_profiler:
        self._serializers_profiler.StartTiming(u'event_tag')

      serialized_event_tag = self._event_tag_serializer.WriteSerialized(tag)

      if self._serializers_profiler:
        self._serializers_profiler.StopTiming(u'event_tag')

      serialized_event_tags.append(serialized_event_tag)

    if self._serializers_profiler:
      self._serializers_profiler.StartTiming(u'write')

    stream_name = u'plaso_tag_index.{0:06d}'.format(tag_number)
    event_tag_index_table = _SerializedEventTagIndexTable(
        self._zipfile, stream_name)

    stream_name = u'plaso_tagging.{0:06d}'.format(tag_number)
    data_stream = _SerializedDataStream(self._zipfile, stream_name)
    entry_data_offset = data_stream.WriteInitialize()

    try:
      for tag_index, tag in enumerate(tags):
        entry_data_offset = data_stream.WriteEntry(
            serialized_event_tags[tag_index])

        event_uuid = getattr(tag, u'event_uuid', None)
        store_number = getattr(tag, u'store_number', None)
        store_offset = getattr(tag, u'store_index', None)

        if event_uuid:
          tag_type = _EventTagIndexValue.TAG_TYPE_UUID
        else:
          tag_type = _EventTagIndexValue.TAG_TYPE_NUMERIC

        event_tag_index_table.AddEventTagIndex(
            tag_type, entry_data_offset, event_uuid=event_uuid,
            store_number=store_number, store_offset=store_offset)

    except:
      data_stream.WriteAbort()

      if self._serializers_profiler:
        self._serializers_profiler.StopTiming(u'write')

      raise

    event_tag_index_table.Write()
    data_stream.WriteFinalize()

    if self._serializers_profiler:
      self._serializers_profiler.StopTiming(u'write')

    # TODO: Update the tags that have changed in the index instead
    # of flushing the index.

    # If we already built a list of tag in memory we need to clear that
    # since the tags have changed.
    if self._event_tag_index is not None:
      del self._event_tag_index