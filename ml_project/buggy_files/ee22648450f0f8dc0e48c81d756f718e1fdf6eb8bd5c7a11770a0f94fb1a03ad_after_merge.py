  def _StartAnalysisProcesses(
      self, knowledge_base_object, storage_writer, analysis_plugins,
      data_location, event_filter_expression=None):
    """Starts the analysis processes.

    Args:
      knowledge_base_object (KnowledgeBase): contains information from
          the source data needed for processing.
      storage_writer (StorageWriter): storage writer.
      analysis_plugins (list[AnalysisPlugin]): analysis plugins that should
          be run.
      data_location (str): path to the location that data files should
          be loaded from.
      event_filter_expression (Optional[str]): event filter expression.
    """
    logging.info(u'Starting analysis plugins.')

    for analysis_plugin in analysis_plugins:
      if self._use_zeromq:
        queue_name = u'{0:s} output event queue'.format(analysis_plugin.NAME)
        output_event_queue = zeromq_queue.ZeroMQPushBindQueue(
            name=queue_name, timeout_seconds=self._QUEUE_TIMEOUT)
        # Open the queue so it can bind to a random port, and we can get the
        # port number to use in the input queue.
        output_event_queue.Open()

      else:
        output_event_queue = multi_process_queue.MultiProcessingQueue(
            timeout=self._QUEUE_TIMEOUT)

      self._event_queues[analysis_plugin.NAME] = output_event_queue

      if self._use_zeromq:
        queue_name = u'{0:s} input event queue'.format(analysis_plugin.NAME)
        input_event_queue = zeromq_queue.ZeroMQPullConnectQueue(
            name=queue_name, delay_open=True, port=output_event_queue.port,
            timeout_seconds=self._QUEUE_TIMEOUT)

      else:
        input_event_queue = output_event_queue

      process = analysis_process.AnalysisProcess(
          input_event_queue, storage_writer, knowledge_base_object,
          analysis_plugin, data_location=data_location,
          event_filter_expression=event_filter_expression,
          name=analysis_plugin.plugin_name)

      process.start()

      logging.info(u'Started analysis plugin: {0:s} (PID: {1:d}).'.format(
          analysis_plugin.plugin_name, process.pid))

      self._RegisterProcess(process)
      self._StartMonitoringProcess(process.pid)

    logging.info(u'Analysis plugins running')