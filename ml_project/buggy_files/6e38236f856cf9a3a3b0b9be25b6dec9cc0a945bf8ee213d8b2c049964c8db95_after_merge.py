  def _FormatDate(self, event_object):
    """Formats the date.

    Args:
      event_object: the event object (instance of EventObject).

     Returns:
       A string containing the value for the date field.
    """
    try:
      date_use = timelib.Timestamp.CopyToDatetime(
          event_object.timestamp, self._output_mediator.timezone,
          raise_error=True)
    except OverflowError as exception:
      logging.error((
          u'Unable to copy {0:d} into a human readable timestamp with error: '
          u'{1:s}. Event {2!s}:{3!s} triggered the exception.').format(
              event_object.timestamp, exception,
              getattr(event_object, u'store_number', u'N/A'),
              getattr(event_object, u'store_index', u'N/A')))
      return u'0000-00-00'
    return u'{0:04d}-{1:02d}-{2:02d}'.format(
        date_use.year, date_use.month, date_use.day)