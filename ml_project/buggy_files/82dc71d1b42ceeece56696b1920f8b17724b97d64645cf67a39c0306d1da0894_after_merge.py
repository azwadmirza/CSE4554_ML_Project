  def ExamineEvent(self, mediator, event):
    """Evaluates whether an event contains the right data for a hash lookup.

    Args:
      mediator (AnalysisMediator): mediates interactions between
          analysis plugins and other components, such as storage and dfvfs.
      event (EventObject): event.
    """
    self._EnsureRequesterStarted()

    path_spec = event.pathspec
    event_uuids = self._event_uuids_by_pathspec[path_spec]
    event_uuids.append(event.uuid)
    if event.data_type not in self.DATA_TYPES:
      return

    if not self._analyzer.lookup_hash:
      return

    lookup_hash = u'{0:s}_hash'.format(self._analyzer.lookup_hash)
    lookup_hash = getattr(event, lookup_hash, None)
    if not lookup_hash:
      display_name = mediator.GetDisplayName(path_spec)
      logging.warning((
          u'Lookup hash attribute: {0:s}_hash missing from event that '
          u'originated from: {1:s}.').format(
              self._analyzer.lookup_hash, display_name))
      return

    path_specs = self._hash_pathspecs[lookup_hash]
    path_specs.append(path_spec)
    # There may be multiple path specification that have the same hash. We only
    # want to look them up once.
    if len(path_specs) == 1:
      self.hash_queue.put(lookup_hash)