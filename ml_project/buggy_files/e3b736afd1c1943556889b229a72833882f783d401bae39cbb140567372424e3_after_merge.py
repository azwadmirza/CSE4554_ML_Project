  def ExamineEvent(self, mediator, event, event_data):
    """Analyzes an event and creates Windows Services as required.

    At present, this method only handles events extracted from the Registry.

    Args:
      mediator (AnalysisMediator): mediates interactions between analysis
          plugins and other components, such as storage and dfvfs.
      event (EventObject): event to examine.
      event_data (EventData): event data.
    """
    # TODO: Handle event log entries here also (ie, event id 4697).
    if event_data.data_type != 'windows:registry:service':
      return

    event_data_attributes = event_data.CopyToDict()
    service_event_data = services.WindowsRegistryServiceEventData()
    service_event_data.CopyFromDict(event_data_attributes)

    service = WindowsService.FromEventData(service_event_data)
    self._service_collection.AddService(service)