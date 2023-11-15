  def ExamineEvent(self, mediator, event, event_data, event_data_stream):
    """Evaluates whether an event contains the right data for a hash lookup.

    Args:
      mediator (AnalysisMediator): mediates interactions between
          analysis plugins and other components, such as storage and dfvfs.
      event (EventObject): event.
      event_data (EventData): event data.
      event_data_stream (EventDataStream): event data stream.
    """
    if (event_data.data_type not in self.DATA_TYPES or
        not self._analyzer.lookup_hash):
      return

    self._EnsureRequesterStarted()

    path_specification = getattr(event_data_stream, 'path_spec', None)
    if not path_specification:
      # Note that support for event_data.pathspec is kept for backwards
      # compatibility.
      path_specification = getattr(event_data, 'pathspec', None)

    event_identifiers = self._event_identifiers_by_path_spec[path_specification]

    event_identifier = event.GetIdentifier()
    event_identifiers.append(event_identifier)

    hash_attributes_container = event_data_stream
    if not hash_attributes_container:
      hash_attributes_container = event_data

    lookup_hash = '{0:s}_hash'.format(self._analyzer.lookup_hash)
    lookup_hash = getattr(hash_attributes_container, lookup_hash, None)
    if not lookup_hash:
      display_name = mediator.GetDisplayNameForPathSpec(path_specification)
      logger.warning((
          'Lookup hash attribute: {0:s}_hash missing from event that '
          'originated from: {1:s}.').format(
              self._analyzer.lookup_hash, display_name))
      return

    path_specs = self._hash_path_specs[lookup_hash]
    path_specs.append(path_specification)
    # There may be multiple path specifications that have the same hash. We only
    # want to look them up once.
    if len(path_specs) == 1:
      self.hash_queue.put(lookup_hash)