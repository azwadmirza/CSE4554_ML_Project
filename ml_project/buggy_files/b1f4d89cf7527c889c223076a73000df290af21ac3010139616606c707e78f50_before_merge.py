  def _FormatDateTime(self, event_object):
    """Formats the date to a datetime object without timezone information.

    Note: timezone information must be removed due to lack of support
    by xlsxwriter and Excel.

    Args:
      event_object: the event object (instance of EventObject).

    Returns:
      A datetime object (instance of datetime.datetime)
      or a string containing 'ERROR' on OverflowError.
    """
    try:
      timestamp = timelib.Timestamp.CopyToDatetime(
          event_object.timestamp, timezone=self._output_mediator.timezone,
          raise_error=True)

      return timestamp.replace(tzinfo=None)

    except OverflowError as exception:
      logging.error((
          u'Unable to copy {0:d} into a human readable timestamp with error: '
          u'{1:s}. Event {2!d}:{3!d} triggered the exception.').format(
              event_object.timestamp, exception,
              getattr(event_object, u'store_number', u'N/A'),
              getattr(event_object, u'store_index', u'N/A')))

      return u'ERROR'