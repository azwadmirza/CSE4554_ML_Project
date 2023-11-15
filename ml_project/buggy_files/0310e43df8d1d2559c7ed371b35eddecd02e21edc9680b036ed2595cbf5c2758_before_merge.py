  def UpdateNumberOfEventSources(
      self, number_of_consumed_sources, number_of_produced_sources):
    """Updates the number of event sources.

    Args:
      number_of_consumed_sources (int): total number of event sources consumed
          by the process.
      number_of_produced_sources (int): total number of event sources produced
          by the process.

    Returns:
      bool: True if either number of event sources has increased.

    Raises:
      ValueError: if the consumer or produced number of event sources is
          smaller than the value of the previous update.
    """
    if number_of_consumed_sources < self.number_of_consumed_sources:
      raise ValueError(
          u'Number of consumed sources smaller than previous update.')

    if number_of_produced_sources < self.number_of_produced_sources:
      raise ValueError(
          u'Number of produced sources smaller than previous update.')

    consumed_sources_delta = (
        number_of_consumed_sources - self.number_of_consumed_sources)

    self.number_of_consumed_sources = number_of_consumed_sources
    self.number_of_consumed_sources_delta = consumed_sources_delta

    produced_sources_delta = (
        number_of_produced_sources - self.number_of_produced_sources)

    self.number_of_produced_sources = number_of_produced_sources
    self.number_of_produced_sources_delta = produced_sources_delta

    return consumed_sources_delta > 0 or produced_sources_delta > 0