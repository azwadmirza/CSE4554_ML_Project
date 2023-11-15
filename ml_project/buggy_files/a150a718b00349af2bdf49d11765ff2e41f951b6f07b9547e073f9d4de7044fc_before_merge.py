  def _Main(self):
    """The main loop."""
    logging.debug(u'Analysis plugin: {0!s} (PID: {1:d}) started'.format(
        self._name, self._pid))

    self._status = definitions.PROCESSING_STATUS_ANALYZING

    task = tasks.Task()
    # TODO: temporary solution.
    task.identifier = self._analysis_plugin.plugin_name

    self._task = task

    storage_writer = self._storage_writer.CreateTaskStorage(task)

    if self._serializers_profiler:
      storage_writer.SetSerializersProfiler(self._serializers_profiler)

    storage_writer.Open()

    self._analysis_mediator = analysis_mediator.AnalysisMediator(
        storage_writer, self._knowledge_base, data_location=self._data_location)

    # TODO: set event_filter_expression in mediator.

    storage_writer.WriteTaskStart()

    try:
      logging.debug(
          u'{0!s} (PID: {1:d}) started monitoring event queue.'.format(
              self._name, self._pid))

      while not self._abort:
        try:
          event = self._event_queue.PopItem()

        except (errors.QueueClose, errors.QueueEmpty) as exception:
          logging.debug(u'ConsumeItems exiting with exception {0:s}.'.format(
              type(exception)))
          break

        if isinstance(event, plaso_queue.QueueAbort):
          logging.debug(u'ConsumeItems exiting, dequeued QueueAbort object.')
          break

        self._ProcessEvent(self._analysis_mediator, event)

        self._number_of_consumed_events += 1

        if self._memory_profiler:
          self._memory_profiler.Sample()

      logging.debug(
          u'{0!s} (PID: {1:d}) stopped monitoring event queue.'.format(
              self._name, self._pid))

      if not self._abort:
        self._status = definitions.PROCESSING_STATUS_REPORTING

        self._analysis_mediator.ProduceAnalysisReport(self._analysis_plugin)

    # All exceptions need to be caught here to prevent the process
    # from being killed by an uncaught exception.
    except Exception as exception:  # pylint: disable=broad-except
      logging.warning(
          u'Unhandled exception in process: {0!s} (PID: {1:d}).'.format(
              self._name, self._pid))
      logging.exception(exception)

      self._abort = True

    finally:
      storage_writer.WriteTaskCompletion(aborted=self._abort)

      storage_writer.Close()

    try:
      self._storage_writer.PrepareMergeTaskStorage(task)
    except IOError:
      pass

    self._analysis_mediator = None
    self._storage_writer = None
    self._task = None

    if self._abort:
      self._status = definitions.PROCESSING_STATUS_ABORTED
    else:
      self._status = definitions.PROCESSING_STATUS_COMPLETED

    logging.debug(u'Analysis plugin: {0!s} (PID: {1:d}) stopped'.format(
        self._name, self._pid))

    try:
      self._event_queue.Close(abort=self._abort)
    except errors.QueueAlreadyClosed:
      logging.error(u'Queue for {0:s} was already closed.'.format(self.name))