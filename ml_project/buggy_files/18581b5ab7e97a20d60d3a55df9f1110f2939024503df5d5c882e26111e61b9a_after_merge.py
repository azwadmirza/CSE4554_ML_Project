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

      event_data_identifier = self._event_data_identifier_mappings.get(
          lookup_key, None)

      if not event_data_identifier:
        event_identifier = event.GetIdentifier()
        event_identifier = event_identifier.CopyToString()

        if lookup_key in self._deserialization_errors:
          reason = 'deserialized'
        else:
          reason = 'found'

        # TODO: store this as an extraction warning so this is preserved
        # in the storage file.
        logger.error((
            'Unable to merge event attribute container: {0:s} since '
            'corresponding event data: {1:s} could not be {2:s}.').format(
                event_identifier, lookup_key, reason))
        return

      event.SetEventDataIdentifier(event_data_identifier)

    # TODO: add event identifier mappings for event tags.

    self._storage_writer.AddEvent(event)