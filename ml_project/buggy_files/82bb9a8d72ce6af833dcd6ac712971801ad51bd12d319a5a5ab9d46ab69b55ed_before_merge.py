  def _FormatDateTime(self, event_object):
    """Formats the date and time in ISO 8601 format.

    Args:
      event_object: the event object (instance of EventObject).

     Returns:
       A string containing the value for the date field.
    """
    try:
      return timelib.Timestamp.CopyToIsoFormat(
          event_object.timestamp, timezone=self._output_mediator.timezone,
          raise_error=True)

    except OverflowError as exception:
      logging.error((
          u'Unable to copy {0:d} into a human readable timestamp with error: '
          u'{1:s}. Event {2!d}:{3!d} triggered the exception.').format(
              event_object.timestamp, exception,
              getattr(event_object, u'store_number', u'N/A'),
              getattr(event_object, u'store_index', u'N/A')))

      return u'0000-00-00T00:00:00'