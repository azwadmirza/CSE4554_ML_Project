  def UpdateForemanStatus(
      self, identifier, status, pid, display_name,
      number_of_consumed_sources, number_of_produced_sources,
      number_of_consumed_events, number_of_produced_events,
      number_of_consumed_event_tags, number_of_produced_event_tags,
      number_of_consumed_errors, number_of_produced_errors,
      number_of_consumed_reports, number_of_produced_reports):
    """Updates the status of the foreman.

    Args:
      identifier (str): foreman identifier.
      status (str): human readable status of the foreman e.g. 'Idle'.
      pid (int): process identifier (PID).
      display_name (str): human readable of the file entry currently being
          processed by the foreman.
      number_of_consumed_sources (int): total number of event sources consumed
          by the foreman.
      number_of_produced_sources (int): total number of event sources produced
          by the foreman.
      number_of_consumed_events (int): total number of events consumed by
          the foreman.
      number_of_produced_events (int): total number of events produced by
          the foreman.
      number_of_consumed_event_tags (int): total number of event tags consumed
          by the foreman.
      number_of_produced_event_tags (int): total number of event tags produced
          by the foreman.
      number_of_consumed_errors (int): total number of errors consumed by
          the foreman.
      number_of_produced_errors (int): total number of errors produced by
          the foreman.
      number_of_consumed_reports (int): total number of event reports consumed
          by the process.
      number_of_produced_reports (int): total number of event reports produced
          by the process.
    """
    if not self.foreman_status:
      self.foreman_status = ProcessStatus()

    self._UpdateProcessStatus(
        self.foreman_status, identifier, status, pid, display_name,
        number_of_consumed_sources, number_of_produced_sources,
        number_of_consumed_events, number_of_produced_events,
        number_of_consumed_event_tags, number_of_produced_event_tags,
        number_of_consumed_errors, number_of_produced_errors,
        number_of_consumed_reports, number_of_produced_reports)