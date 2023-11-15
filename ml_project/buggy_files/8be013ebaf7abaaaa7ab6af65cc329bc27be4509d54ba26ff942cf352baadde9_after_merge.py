  def _FormatStatusTableRow(
      self, identifier, pid, status, process_status, number_of_events,
      number_of_events_delta, display_name):
    """Formats a status table row.

    Args:
      identifier: identifier to describe the status table entry.
      pid: the process identifier (PID).
      status: the process status string.
      process_status: string containing the process status.
      number_of_events: the total number of events.
      number_of_events_delta: the number of events since the last status update.
      display_name: the display name of the file last processed.
    """
    if (number_of_events_delta == 0 and
        status in [definitions.PROCESSING_STATUS_RUNNING,
                   definitions.PROCESSING_STATUS_HASHING,
                   definitions.PROCESSING_STATUS_PARSING]):
      status = process_status

    # This check makes sure the columns are tab aligned.
    if len(status) < 8:
      status = u'{0:s}\t'.format(status)

    if number_of_events is None or number_of_events_delta is None:
      events = u''
    else:
      events = u'{0:d} ({1:d})'.format(number_of_events, number_of_events_delta)

      # This check makes sure the columns are tab aligned.
      if len(events) < 8:
        events = u'{0:s}\t'.format(events)

    # TODO: shorten display name to fit in 80 chars and show the filename.
    return u'{0:s}\t{1:d}\t{2:s}\t{3:s}\t{4:s}'.format(
        identifier, pid, status, events, display_name)