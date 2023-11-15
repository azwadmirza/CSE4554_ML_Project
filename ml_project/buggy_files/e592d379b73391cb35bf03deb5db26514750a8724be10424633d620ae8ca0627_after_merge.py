  def ProcessStorage(
      self, output_module, storage_file, analysis_plugins,
      event_queue_producers, deduplicate_events=True,
      preferred_encoding=u'utf-8', time_slice=None, use_time_slicer=False):
    """Processes a plaso storage file.

    Args:
      output_module: an output module (instance of OutputModule).
      storage_file: the storage file object (instance of StorageFile).
      analysis_plugins: list of analysis plugin objects (instance of
                        AnalysisPlugin).
      event_queue_producers: list of event queue producer objects (instance
                             of ItemQueueProducer).
      deduplicate_events: optional boolean value to indicate if the event
                          objects should be deduplicated. The default is True.
      preferred_encoding: optional preferred encoding. The default is "utf-8".
      time_slice: optional time slice object (instance of TimeSlice).
                  The default is None.
      use_time_slicer: optional boolean value to indicate the 'time slicer'
                       should be used. The default is False. The 'time slicer'
                       will provide a context of events around an event of
                       interest.

    Returns:
      A counter (an instance of counter.Counter) that contains the analysis
      plugin results or None.

    Raises:
      RuntimeError: if a non-recoverable situation is encountered.
    """
    if time_slice:
      if time_slice.event_timestamp:
        pfilter.TimeRangeCache.SetLowerTimestamp(time_slice.start_timestamp)
        pfilter.TimeRangeCache.SetUpperTimestamp(time_slice.end_timestamp)

      elif use_time_slicer:
        self._filter_buffer = bufferlib.CircularBuffer(time_slice.duration)

    counter = None
    with storage_file:
      storage_file.SetStoreLimit(self._filter_object)

      # TODO: allow for single processing.
      # TODO: add upper queue limit.
      analysis_output_queue = multi_process.MultiProcessingQueue(timeout=5)

      if analysis_plugins:
        logging.info(u'Starting analysis plugins.')
        # Within all preprocessing objects, try to get the last one that has
        # time zone information stored in it, the highest chance of it
        # containing the information we are seeking (defaulting to the last
        # one).
        pre_objs = storage_file.GetStorageInformation()
        pre_obj = pre_objs[-1]
        for obj in pre_objs:
          if getattr(obj, u'time_zone_str', u''):
            pre_obj = obj

        # Fill in the collection information.
        pre_obj.collection_information = {}
        if preferred_encoding:
          cmd_line = u' '.join(sys.argv)
          try:
            pre_obj.collection_information[u'cmd_line'] = cmd_line.decode(
                preferred_encoding)
          except UnicodeDecodeError:
            pass
        pre_obj.collection_information[u'file_processed'] = (
            self._storage_file_path)
        pre_obj.collection_information[u'method'] = u'Running Analysis Plugins'
        analysis_plugin_names = [plugin.NAME for plugin in analysis_plugins]
        pre_obj.collection_information[u'plugins'] = analysis_plugin_names
        time_of_run = timelib.Timestamp.GetNow()
        pre_obj.collection_information[u'time_of_run'] = time_of_run

        pre_obj.counter = collections.Counter()

        # Assign the preprocessing object to the storage.
        # This is normally done in the construction of the storage object,
        # however we cannot do that here since the preprocessing object is
        # stored inside the storage file, so we need to open it first to
        # be able to read it in, before we make changes to it. Thus we need
        # to access this protected member of the class.
        # pylint: disable=protected-access
        storage_file._pre_obj = pre_obj

        knowledge_base_object = knowledge_base.KnowledgeBase(pre_obj=pre_obj)

        # Now we need to start all the plugins.
        for analysis_plugin in analysis_plugins:
          analysis_report_queue_producer = queue.ItemQueueProducer(
              analysis_output_queue)

          completion_event = multiprocessing.Event()
          analysis_mediator_object = analysis_mediator.AnalysisMediator(
              analysis_report_queue_producer, knowledge_base_object,
              data_location=self._data_location,
              completion_event=completion_event)
          analysis_process = multiprocessing.Process(
              name=u'Analysis {0:s}'.format(analysis_plugin.plugin_name),
              target=analysis_plugin.RunPlugin,
              args=(analysis_mediator_object,))
          process_info = PsortAnalysisProcess(
              completion_event, analysis_plugin, analysis_process)
          self._analysis_process_info.append(process_info)

          analysis_process.start()
          logging.info(
              u'Plugin: [{0:s}] started.'.format(analysis_plugin.plugin_name))
      else:
        event_queue_producers = []

      output_buffer = output_interface.EventBuffer(
          output_module, deduplicate_events)
      with output_buffer:
        counter = self.ProcessOutput(
            storage_file, output_buffer, my_filter=self._filter_object,
            filter_buffer=self._filter_buffer,
            analysis_queues=event_queue_producers)

      for information in storage_file.GetStorageInformation():
        if hasattr(information, u'counter'):
          counter[u'Stored Events'] += information.counter[u'total']

      if not self._quiet_mode:
        logging.info(u'Output processing is done.')

      # Get all reports and tags from analysis plugins.
      self._ProcessAnalysisPlugins(
          analysis_plugins, analysis_output_queue, storage_file, counter,
          preferred_encoding=preferred_encoding)

    if self._output_file_object:
      self._output_file_object.close()
      self._output_file_object = None

    if self._filter_object and not counter[u'Limited By']:
      counter[u'Filter By Date'] = (
          counter[u'Stored Events'] - counter[u'Events Included'] -
          counter[u'Events Filtered Out'])

    return counter