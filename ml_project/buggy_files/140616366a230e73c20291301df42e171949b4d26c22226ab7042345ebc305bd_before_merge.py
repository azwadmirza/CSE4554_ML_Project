  def AddEventObject(self, event_object):
    """Adds an event object to the storage.

    Args:
      event_object: an event object (instance of EventObject).

    Raises:
      IOError: When trying to write to a closed storage file.
    """
    if not self._zipfile:
      raise IOError(u'Trying to add an entry to a closed storage file.')

    if event_object.timestamp > self._buffer_last_timestamp:
      self._buffer_last_timestamp = event_object.timestamp

    # TODO: support negative timestamps.
    if (event_object.timestamp < self._buffer_first_timestamp and
        event_object.timestamp > 0):
      self._buffer_first_timestamp = event_object.timestamp

    attributes = event_object.GetValues()
    # Add values to counters.
    if self._pre_obj:
      self._pre_obj.counter[u'total'] += 1
      self._pre_obj.counter[attributes.get(u'parser', u'N/A')] += 1
      # TODO remove plugin, add parser chain. Refactor to separate method e.g.
      # UpdateEventCounters.
      if u'plugin' in attributes:
        self._pre_obj.plugin_counter[attributes.get(u'plugin', u'N/A')] += 1

    # Add to temporary counter.
    self._count_data_type[event_object.data_type] += 1
    parser = attributes.get(u'parser', u'unknown_parser')
    self._count_parser[parser] += 1

    if self._serializers_profiler:
      self._serializers_profiler.StartTiming(u'event_object')

    event_object_data = self._event_object_serializer.WriteSerialized(
        event_object)

    if self._serializers_profiler:
      self._serializers_profiler.StopTiming(u'event_object')

    # TODO: Re-think this approach with the re-design of the storage.
    # Check if the event object failed to serialize (none is returned).
    if event_object_data is None:
      return

    heapq.heappush(
        self._buffer, (event_object.timestamp, event_object_data))
    self._buffer_size += len(event_object_data)
    self._write_counter += 1

    if self._buffer_size > self._max_buffer_size:
      self._WriteBuffer()