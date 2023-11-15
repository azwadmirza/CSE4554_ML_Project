  def UpdateNumberOfErrors(
      self, number_of_consumed_errors, number_of_produced_errors):
    """Updates the number of errors.

    Args:
      number_of_consumed_errors (int): total number of errors consumed by
          the process.
      number_of_produced_errors (int): total number of errors produced by
          the process.

    Returns:
      bool: True if either number of errors has increased.

    Raises:
      ValueError: if the consumer or produced number of errors is smaller
          than the value of the previous update.
    """
    if number_of_consumed_errors < self.number_of_consumed_errors:
      raise ValueError(
          u'Number of consumed errors smaller than previous update.')

    if number_of_produced_errors < self.number_of_produced_errors:
      raise ValueError(
          u'Number of produced errors smaller than previous update.')

    consumed_errors_delta = (
        number_of_consumed_errors - self.number_of_consumed_errors)

    self.number_of_consumed_errors = number_of_consumed_errors
    self.number_of_consumed_errors_delta = consumed_errors_delta

    produced_errors_delta = (
        number_of_produced_errors - self.number_of_produced_errors)

    self.number_of_produced_errors = number_of_produced_errors
    self.number_of_produced_errors_delta = produced_errors_delta

    return consumed_errors_delta > 0 or produced_errors_delta > 0