  def AddEventTag(self, event_tag):
    """Adds an event tag.

    Args:
      event_tag: an event tag object (instance of EventTag).

    Raises:
      IOError: when the storage writer is closed.
    """
    if not self._storage_file:
      raise IOError(u'Unable to write to closed storage writer.')

    self._storage_file.AddEventTag(event_tag)

    self._session.event_labels_counter[u'total'] += 1
    for label in event_tag.labels:
      self._session.event_labels_counter[label] += 1
    self.number_of_event_tags += 1