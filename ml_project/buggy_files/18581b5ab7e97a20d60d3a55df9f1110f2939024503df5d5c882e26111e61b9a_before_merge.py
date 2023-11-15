  def _AddEvent(self, event, serialized_data=None):
    """Adds an event.

    Args:
      event (EventObject): event.
      serialized_data (Optional[bytes]): serialized form of the event.
    """
    if hasattr(event, 'event_data_row_identifier'):
      event_data_identifier = identifiers.SQLTableIdentifier(
          self._CONTAINER_TYPE_EVENT_DATA,
          event.event_data_row_identifier)
      lookup_key = event_data_identifier.CopyToString()

      event_data_identifier = self._event_data_identifier_mappings[lookup_key]
      event.SetEventDataIdentifier(event_data_identifier)

    # TODO: add event identifier mappings for event tags.

    self._storage_writer.AddEvent(event)