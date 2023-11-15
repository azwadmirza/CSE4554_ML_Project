  def GetAnalysisPluginsAndEventQueues(self, analysis_plugins_string):
    """Return a list of analysis plugins and event queues.

    Args:
      analysis_plugins_string: comma separated string with names of analysis
                               plugins to load.

    Returns:
      A tuple of two lists, one containing list of analysis plugins
      and the other a list of event queues.
    """
    if not analysis_plugins_string:
      return [], []

    # Start queues and load up plugins.
    event_queue_producers = []
    event_queues = []
    analysis_plugins_list = [
        name.strip() for name in analysis_plugins_string.split(u',')]

    for _ in range(0, len(analysis_plugins_list)):
      # TODO: add upper queue limit.
      analysis_plugin_queue = multi_process.MultiProcessingQueue(timeout=5)
      event_queues.append(analysis_plugin_queue)
      event_queue_producers.append(
          queue.ItemQueueProducer(event_queues[-1]))

    analysis_plugins = analysis_manager.AnalysisPluginManager.LoadPlugins(
        analysis_plugins_list, event_queues)

    analysis_plugins = list(analysis_plugins)

    return analysis_plugins, event_queue_producers