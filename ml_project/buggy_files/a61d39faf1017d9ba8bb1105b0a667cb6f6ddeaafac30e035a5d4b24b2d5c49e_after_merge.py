  def _GetStatus(self):
    """Returns a status dictionary.

    Returns:
      dict [str, object]: status attributes, indexed by name.
    """
    if self._parser_mediator:
      number_of_produced_errors = (
          self._parser_mediator.number_of_produced_errors)
      number_of_produced_events = (
          self._parser_mediator.number_of_produced_events)
      number_of_produced_sources = (
          self._parser_mediator.number_of_produced_event_sources)
    else:
      number_of_produced_errors = None
      number_of_produced_events = None
      number_of_produced_sources = None

    if self._extraction_worker:
      processing_status = self._extraction_worker.processing_status
    else:
      processing_status = self._status

    status = {
        u'display_name': self._current_display_name,
        u'identifier': self._name,
        u'number_of_consumed_errors': None,
        u'number_of_consumed_events': self._number_of_consumed_events,
        u'number_of_consumed_sources': self._number_of_consumed_sources,
        u'number_of_produced_errors': number_of_produced_errors,
        u'number_of_produced_events': number_of_produced_events,
        u'number_of_produced_sources': number_of_produced_sources,
        u'processing_status': processing_status,
        u'task_identifier': self._task_identifier}

    self._status_is_running = status.get(u'is_running', False)
    return status