  def _ProcessAnalysisPlugins(
      self, analysis_plugins, analysis_output_queue, storage_file, counter,
      preferred_encoding=u'utf-8'):
    """Runs the analysis plugins.

    Args:
      analysis_plugins: the analysis plugins.
      analysis_output_queue: the analysis output queue (instance of Queue).
      storage_file: a storage file object (instance of StorageFile).
      counter: a counter object (instance of collections.Counter).
      preferred_encoding: optional preferred encoding. The default is "utf-8".
    """
    if not analysis_plugins:
      return

    logging.info(u'Processing data from analysis plugins.')

    # Wait for all analysis plugins to complete.
    for analysis_process_info in self._analysis_process_info:
      name = analysis_process_info.plugin.NAME
      if analysis_process_info.plugin.LONG_RUNNING_PLUGIN:
        logging.warning(
            u'{0:s} may take a long time to run. It will not be automatically '
            u'terminated.'.format(name))
        report_wait = None
      else:
        report_wait = self.MAX_ANALYSIS_PLUGIN_REPORT_WAIT
      completion_event = analysis_process_info.completion_event
      logging.info(
          u'Waiting for analysis plugin: {0:s} to complete.'.format(name))
      if completion_event.wait(report_wait):
        logging.info(u'Plugin {0:s} has completed.'.format(name))
      else:
        logging.warning(
            u'Analysis process {0:s} failed to compile its report in a '
            u'reasonable time. No report will be displayed or stored.'.format(
                name))

    logging.info(u'All analysis plugins are now completed.')

    # Go over each output.
    analysis_queue_consumer = PsortAnalysisReportQueueConsumer(
        analysis_output_queue, storage_file, self._filter_expression,
        preferred_encoding=preferred_encoding)

    analysis_queue_consumer.ConsumeItems()

    if analysis_queue_consumer.tags:
      storage_file.StoreTagging(analysis_queue_consumer.tags)

    # TODO: analysis_queue_consumer.anomalies:

    for item, value in analysis_queue_consumer.counter.iteritems():
      counter[item] = value