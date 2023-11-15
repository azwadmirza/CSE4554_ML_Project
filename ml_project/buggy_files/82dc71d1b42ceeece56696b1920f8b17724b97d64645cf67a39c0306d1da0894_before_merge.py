  def ExamineEvent(self, mediator, event):
    """Evaluates whether an event contains the right data for a hash lookup.

    Args:
      mediator (AnalysisMediator): mediates interactions between
          analysis plugins and other components, such as storage and dfvfs.
      event (EventObject): event.
    """
    self._EnsureRequesterStarted()
    pathspec = event.pathspec
    event_uuids = self._event_uuids_by_pathspec[pathspec]
    event_uuids.append(event.uuid)
    if event.data_type in self.DATA_TYPES:
      for attribute in self.REQUIRED_HASH_ATTRIBUTES:
        hash_for_lookup = getattr(event, attribute, None)
        if not hash_for_lookup:
          continue
        pathspecs = self._hash_pathspecs[hash_for_lookup]
        pathspecs.append(pathspec)
        # There may be multiple pathspecs that have the same hash. We only
        # want to look them up once.
        if len(pathspecs) == 1:
          self.hash_queue.put(hash_for_lookup)
        return
      warning_message = (
          u'Event with ID {0:s} had none of the required attributes '
          u'{1:s}.').format(
              event.uuid, self.REQUIRED_HASH_ATTRIBUTES)
      logging.warning(warning_message)