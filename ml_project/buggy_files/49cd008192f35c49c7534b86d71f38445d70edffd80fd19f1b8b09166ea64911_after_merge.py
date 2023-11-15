  def _AnalyzeEvents(self, storage_writer, analysis_plugins, event_filter=None):
    """Analyzes events in a plaso storage.

    Args:
      storage_writer (StorageWriter): storage writer.
      analysis_plugins (list[AnalysisPlugin]): analysis plugins that should
          be run.
      event_filter (Optional[FilterObject]): event filter.

    Raises:
      RuntimeError: if a non-recoverable situation is encountered.
    """
    self._status = definitions.PROCESSING_STATUS_RUNNING
    self._number_of_consumed_errors = 0
    self._number_of_consumed_events = 0
    self._number_of_consumed_reports = 0
    self._number_of_consumed_sources = 0
    self._number_of_produced_errors = 0
    self._number_of_produced_events = 0
    self._number_of_produced_reports = 0
    self._number_of_produced_sources = 0

    number_of_filtered_events = 0

    logging.debug(u'Processing events.')

    filter_limit = getattr(event_filter, u'limit', None)

    for event in storage_writer.GetEvents():
      if event_filter:
        filter_match = event_filter.Match(event)
      else:
        filter_match = None

      # pylint: disable=singleton-comparison
      if filter_match == False:
        number_of_filtered_events += 1
        continue

      for event_queue in self._event_queues.values():
        # TODO: Check for premature exit of analysis plugins.
        event_queue.PushItem(event)

      self._number_of_consumed_events += 1

      if (event_filter and filter_limit and
          filter_limit == self._number_of_consumed_events):
        break

    logging.debug(u'Finished pushing events to analysis plugins.')
    # Signal that we have finished adding events.
    for event_queue in self._event_queues.values():
      event_queue.PushItem(plaso_queue.QueueAbort(), block=False)

    logging.debug(u'Processing analysis plugin results.')

    # TODO: use a task based approach.
    plugin_names = [plugin.plugin_name for plugin in analysis_plugins]
    while plugin_names:
      for plugin_name in list(plugin_names):
        if self._abort:
          break

        # TODO: temporary solution.
        task = tasks.Task()
        task.identifier = plugin_name

        merge_ready = storage_writer.CheckTaskReadyForMerge(task)
        if merge_ready:
          self._status = definitions.PROCESSING_STATUS_MERGING

          event_queue = self._event_queues[plugin_name]
          del self._event_queues[plugin_name]

          event_queue.Close()

          storage_merge_reader = storage_writer.StartMergeTaskStorage(task)

          storage_merge_reader.MergeAttributeContainers()
          # TODO: temporary solution.
          plugin_names.remove(plugin_name)

          self._status = definitions.PROCESSING_STATUS_RUNNING

          self._number_of_produced_event_tags = (
              storage_writer.number_of_event_tags)
          self._number_of_produced_reports = (
              storage_writer.number_of_analysis_reports)

    try:
      storage_writer.StopTaskStorage(abort=self._abort)
    except (IOError, OSError) as exception:
      logging.error(u'Unable to stop task storage with error: {0:s}'.format(
          exception))

    if self._abort:
      logging.debug(u'Processing aborted.')
    else:
      logging.debug(u'Processing completed.')

    events_counter = collections.Counter()
    events_counter[u'Events filtered'] = number_of_filtered_events
    events_counter[u'Events processed'] = self._number_of_consumed_events

    return events_counter