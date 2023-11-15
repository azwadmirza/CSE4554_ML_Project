  def ExamineEvent(self, mediator, event, event_data):
    """Analyzes an event and creates Windows Services as required.

    At present, this method only handles events extracted from the Registry.

    Args:
      mediator (AnalysisMediator): mediates interactions between analysis
          plugins and other components, such as storage and dfvfs.
      event (EventObject): event to examine.
      event_data (EventData): event data.
    """
    if event_data.data_type not in self._SUPPORTED_EVENT_DATA_TYPES:
      return

    # TODO: Handle event log entries here also (ie, event id 4697).
    service = WindowsService.FromEventData(event_data)
    self._service_collection.AddService(service)