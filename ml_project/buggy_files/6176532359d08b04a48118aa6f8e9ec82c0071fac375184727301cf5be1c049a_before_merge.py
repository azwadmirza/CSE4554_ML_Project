  def _ExportEvents(
      self, storage_reader, event_buffer, event_filter=None, time_slice=None,
      use_time_slicer=False):
    """Exports events using an output module.

    Args:
      storage_reader (StorageReader): storage reader.
      event_buffer (EventBuffer): event buffer.
      event_filter (Optional[FilterObject]): event filter.
      time_slice (Optional[TimeRange]): time range that defines a time slice
          to filter events.
      use_time_slicer (Optional[bool]): True if the 'time slicer' should be
          used. The 'time slicer' will provide a context of events around
          an event of interest.

    Returns:
      collections.Counter: counter that tracks the number of unique events
          read from storage.
    """
    time_slice_buffer = None
    if time_slice:
      if time_slice.event_timestamp is not None:
        time_slice = storage_time_range.TimeRange(
            time_slice.start_timestamp, time_slice.end_timestamp)

      if use_time_slicer:
        time_slice_buffer = bufferlib.CircularBuffer(time_slice.duration)

    filter_limit = getattr(event_filter, u'limit', None)
    forward_entries = 0

    number_of_filtered_events = 0
    number_of_events_from_time_slice = 0

    for event in storage_reader.GetEvents(time_range=time_slice):
      if event_filter:
        filter_match = event_filter.Match(event)
      else:
        filter_match = None

      # pylint: disable=singleton-comparison
      if filter_match == False:
        if not time_slice_buffer:
          number_of_filtered_events += 1

        elif forward_entries == 0:
          time_slice_buffer.Append(event)
          number_of_filtered_events += 1

        elif forward_entries <= time_slice_buffer.size:
          event_buffer.Append(event)
          self._number_of_consumed_events += 1
          number_of_events_from_time_slice += 1
          forward_entries += 1

        else:
          # We reached the maximum size of the time slice and don't need to
          # include other entries.
          number_of_filtered_events += 1
          forward_entries = 0

      else:
        # pylint: disable=singleton-comparison
        if filter_match == True and time_slice_buffer:
          # Empty the time slice buffer.
          for event_in_buffer in time_slice_buffer.Flush():
            event_buffer.Append(event_in_buffer)
            self._number_of_consumed_events += 1
            number_of_filtered_events += 1
            number_of_events_from_time_slice += 1

          forward_entries = 1

        event_buffer.Append(event)
        self._number_of_consumed_events += 1

        # pylint: disable=singleton-comparison
        if (filter_match == True and filter_limit and
            filter_limit == self._number_of_consumed_events):
          break

    events_counter = collections.Counter()
    events_counter[u'Events filtered'] = number_of_filtered_events
    events_counter[u'Events from time slice'] = number_of_events_from_time_slice
    events_counter[u'Events processed'] = self._number_of_consumed_events

    if event_buffer.duplicate_counter:
      events_counter[u'Duplicate events removed'] = (
          event_buffer.duplicate_counter)

    if filter_limit:
      events_counter[u'Limited By'] = filter_limit

    return events_counter