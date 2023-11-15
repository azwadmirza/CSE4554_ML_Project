  def _GetStatus(self):
    """Returns status information.

    Returns:
      dict[str, object]: status attributes, indexed by name.
    """
    if self._analysis_mediator:
      number_of_produced_event_tags = (
          self._analysis_mediator.number_of_produced_event_tags)
      number_of_produced_reports = (
          self._analysis_mediator.number_of_produced_analysis_reports)
    else:
      number_of_produced_event_tags = None
      number_of_produced_reports = None

    status = {
        u'display_name': u'',
        u'identifier': self._name,
        u'number_of_consumed_errors': None,
        u'number_of_consumed_event_tags': None,
        u'number_of_consumed_events': self._number_of_consumed_events,
        u'number_of_consumed_reports': None,
        u'number_of_consumed_sources': None,
        u'number_of_produced_errors': None,
        u'number_of_produced_event_tags': number_of_produced_event_tags,
        u'number_of_produced_events': None,
        u'number_of_produced_reports': number_of_produced_reports,
        u'number_of_produced_sources': None,
        u'processing_status': self._status,
        u'task_identifier': None}

    if self._status in (
        definitions.PROCESSING_STATUS_ABORTED,
        definitions.PROCESSING_STATUS_COMPLETED):
      self._foreman_status_wait_event.set()

    return status