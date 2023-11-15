  def _UpdateProcessStatus(
      self, process_status, identifier, status, pid, display_name,
      number_of_consumed_sources, number_of_produced_sources,
      number_of_consumed_events, number_of_produced_events,
      number_of_consumed_errors, number_of_produced_errors,
      number_of_consumed_reports, number_of_produced_reports):
    """Updates a process status.

    Args:
      process_status (ProcessStatus): process status.
      identifier (str): process identifier.
      status (str): human readable status of the process e.g. 'Idle'.
      pid (int): process identifier (PID).
      display_name (str): human readable of the file entry currently being
          processed by the process.
      number_of_consumed_sources (int): total number of event sources consumed
          by the process.
      number_of_produced_sources (int): total number of event sources produced
          by the process.
      number_of_consumed_events (int): total number of events consumed by
          the process.
      number_of_produced_events (int): total number of events produced by
          the process.
      number_of_consumed_errors (int): total number of errors consumed by
          the process.
      number_of_produced_errors (int): total number of errors produced by
          the process.
      number_of_consumed_reports (int): total number of event reports consumed
          by the process.
      number_of_produced_reports (int): total number of event reports produced
          by the process.
    """
    new_sources = process_status.UpdateNumberOfEventSources(
        number_of_consumed_sources, number_of_produced_sources)

    new_events = process_status.UpdateNumberOfEvents(
        number_of_consumed_events, number_of_produced_events)

    new_errors = process_status.UpdateNumberOfErrors(
        number_of_consumed_errors, number_of_produced_errors)

    new_reports = process_status.UpdateNumberOfEventReports(
        number_of_consumed_reports, number_of_produced_reports)

    process_status.display_name = display_name
    process_status.identifier = identifier
    process_status.pid = pid
    process_status.status = status

    if new_sources or new_events or new_errors or new_reports:
      process_status.last_running_time = time.time()