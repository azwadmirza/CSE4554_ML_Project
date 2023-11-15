  def ProduceEventWithEventData(self, event, event_data):
    """Produces an event.

    Args:
      event (EventObject): event.
      event_data (EventData): event data.

    Raises:
      InvalidEvent: if the event timestamp value is not set or out of bounds or
          if the event data (attribute container) values cannot be hashed.
    """
    if event.timestamp is None:
      raise errors.InvalidEvent('Event timestamp value not set.')

    if event.timestamp < self._INT64_MIN or event.timestamp > self._INT64_MAX:
      raise errors.InvalidEvent('Event timestamp value out of bounds.')

    try:
      event_data_hash = event_data.GetAttributeValuesHash()
    except TypeError as exception:
      raise errors.InvalidEvent(
          'Unable to hash event data values with error: {0!s}'.format(
              exception))

    if event_data_hash != self._last_event_data_hash:
      # Make a copy of the event data before adding additional values.
      event_data = copy.deepcopy(event_data)

      self.ProcessEventData(
          event_data, parser_chain=self.GetParserChain(),
          file_entry=self._file_entry)

      self._storage_writer.AddEventData(event_data)

      self._last_event_data_hash = event_data_hash
      self._last_event_data_identifier = event_data.GetIdentifier()

    if self._last_event_data_identifier:
      event.SetEventDataIdentifier(self._last_event_data_identifier)

    # TODO: remove this after structural fix is in place
    # https://github.com/log2timeline/plaso/issues/1691
    event.parser = self.GetParserChain()

    self._storage_writer.AddEvent(event)
    self._number_of_events += 1

    self.last_activity_timestamp = time.time()