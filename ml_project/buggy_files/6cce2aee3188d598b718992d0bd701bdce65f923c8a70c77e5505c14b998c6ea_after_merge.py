  def _FormatStatusTableRow(self, process_status):
    """Formats a status table row.

    Args:
      process_status (ProcessStatus): processing status.
    """
    # This check makes sure the columns are tab aligned.
    identifier = process_status.identifier
    if len(identifier) < 8:
      identifier = u'{0:s}\t\t'.format(identifier)
    elif len(identifier) < 16:
      identifier = u'{0:s}\t'.format(identifier)

    status = process_status.status
    if len(status) < 8:
      status = u'{0:s}\t'.format(status)

    events = u''
    if (process_status.number_of_consumed_events is not None and
        process_status.number_of_consumed_events_delta is not None):
      events = u'{0:d} ({1:d})'.format(
          process_status.number_of_consumed_events,
          process_status.number_of_consumed_events_delta)

    # This check makes sure the columns are tab aligned.
    if len(events) < 8:
      events = u'{0:s}\t'.format(events)

    event_tags = u''
    if (process_status.number_of_produced_event_tags is not None and
        process_status.number_of_produced_event_tags_delta is not None):
      event_tags = u'{0:d} ({1:d})'.format(
          process_status.number_of_produced_event_tags,
          process_status.number_of_produced_event_tags_delta)

    # This check makes sure the columns are tab aligned.
    if len(event_tags) < 8:
      event_tags = u'{0:s}\t'.format(event_tags)

    reports = u''
    if (process_status.number_of_produced_reports is not None and
        process_status.number_of_produced_reports_delta is not None):
      reports = u'{0:d} ({1:d})'.format(
          process_status.number_of_produced_reports,
          process_status.number_of_produced_reports_delta)

    # This check makes sure the columns are tab aligned.
    if len(reports) < 8:
      reports = u'{0:s}\t'.format(reports)

    # TODO: shorten display name to fit in 80 chars and show the filename.
    return u'{0:s}\t{1:d}\t{2:s}\t{3:s}\t{4:s}\t{5:s}'.format(
        identifier, process_status.pid, status, events, event_tags, reports)