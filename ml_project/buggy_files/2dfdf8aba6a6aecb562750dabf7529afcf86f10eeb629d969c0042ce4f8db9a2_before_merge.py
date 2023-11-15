  def UpdateNumberOfEvents(
      self, number_of_consumed_events, number_of_produced_events):
    """Updates the number of events.

    Args:
      number_of_consumed_events (int): total number of events consumed by
          the process.
      number_of_produced_events (int): total number of events produced by
          the process.

    Returns:
      bool: True if either number of events has increased.

    Raises:
      ValueError: if the consumer or produced number of events is smaller
          than the value of the previous update.
    """
    if number_of_consumed_events < self.number_of_consumed_events:
      raise ValueError(
          u'Number of consumed events smaller than previous update.')

    if number_of_produced_events < self.number_of_produced_events:
      raise ValueError(
          u'Number of produced events smaller than previous update.')

    consumed_events_delta = (
        number_of_consumed_events - self.number_of_consumed_events)

    self.number_of_consumed_events = number_of_consumed_events
    self.number_of_consumed_events_delta = consumed_events_delta

    produced_events_delta = (
        number_of_produced_events - self.number_of_produced_events)

    self.number_of_produced_events = number_of_produced_events
    self.number_of_produced_events_delta = produced_events_delta

    return consumed_events_delta > 0 or produced_events_delta > 0