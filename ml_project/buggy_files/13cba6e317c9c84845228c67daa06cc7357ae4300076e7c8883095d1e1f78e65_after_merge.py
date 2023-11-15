  def _ProcessEvent(self, mediator, event, event_data, event_data_stream):
    """Processes an event.

    Args:
      mediator (AnalysisMediator): mediates interactions between
          analysis plugins and other components, such as storage and dfvfs.
      event (EventObject): event.
      event_data (EventData): event data.
      event_data_stream (EventDataStream): event data stream.
    """
    try:
      self._analysis_plugin.ExamineEvent(
          mediator, event, event_data, event_data_stream)

    except Exception as exception:  # pylint: disable=broad-except
      # TODO: write analysis error and change logger to debug only.

      logger.warning('Unhandled exception while processing event object.')
      logger.exception(exception)