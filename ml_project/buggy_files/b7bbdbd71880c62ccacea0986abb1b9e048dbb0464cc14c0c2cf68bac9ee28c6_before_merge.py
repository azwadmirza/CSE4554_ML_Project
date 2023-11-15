  def ExportEvents(
      self, knowledge_base_object, storage_reader, output_module,
      deduplicate_events=True, event_filter=None, status_update_callback=None,
      time_slice=None, use_time_slicer=False):
    """Exports events using an output module.

    Args:
      knowledge_base_object (KnowledgeBase): contains information from
          the source data needed for processing.
      storage_reader (StorageReader): storage reader.
      output_module (OutputModule): output module.
      deduplicate_events (Optional[bool]): True if events should be
          deduplicated.
      event_filter (Optional[FilterObject]): event filter.
      status_update_callback (Optional[function]): callback function for status
          updates.
      time_slice (Optional[TimeSlice]): slice of time to output.
      use_time_slicer (Optional[bool]): True if the 'time slicer' should be
          used. The 'time slicer' will provide a context of events around
          an event of interest.

    Returns:
      collections.Counter: counter that tracks the number of events extracted
          from storage.
    """
    self._status_update_callback = status_update_callback

    storage_reader.ReadPreprocessingInformation(knowledge_base_object)

    event_buffer = output_event_buffer.EventBuffer(
        output_module, deduplicate_events)

    with event_buffer:
      events_counter = self._ExportEvents(
          storage_reader, event_buffer, event_filter=event_filter,
          time_slice=time_slice, use_time_slicer=use_time_slicer)

    # Reset values.
    self._status_update_callback = None

    return events_counter