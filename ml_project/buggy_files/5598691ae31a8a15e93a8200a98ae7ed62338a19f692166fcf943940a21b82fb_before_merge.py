  def ParseLine(self, parser_mediator):
    """Return an event object extracted from the current line.

    Args:
      parser_mediator: A parser mediator object (instance of ParserMediator).
    """
    if not self.attributes['time']:
      raise errors.TimestampNotCorrectlyFormed(
          u'Unable to parse timestamp, time not set.')

    if not self.attributes['iyear']:
      raise errors.TimestampNotCorrectlyFormed(
          u'Unable to parse timestamp, year not set.')

    times = self.attributes['time'].split(':')
    if self.local_zone:
      timezone = parser_mediator.timezone
    else:
      timezone = pytz.UTC

    if len(times) < 3:
      raise errors.TimestampNotCorrectlyFormed((
          u'Unable to parse timestamp, not of the format HH:MM:SS '
          u'[{0:s}]').format(self.PrintLine()))
    try:
      secs = times[2].split('.')
      if len(secs) == 2:
        sec, us = secs
      else:
        sec = times[2]
        us = 0

      timestamp = timelib.Timestamp.FromTimeParts(
          int(self.attributes['iyear']), self.attributes['imonth'],
          self.attributes['iday'], int(times[0]), int(times[1]),
          int(sec), microseconds=int(us), timezone=timezone)

    except ValueError as exception:
      raise errors.TimestampNotCorrectlyFormed(
          u'Unable to parse: {0:s} with error: {1:s}'.format(
              self.PrintLine(), exception))

    event_object = self.CreateEvent(
        timestamp, getattr(self, 'entry_offset', 0), self.attributes)
    parser_mediator.ProduceEvent(event_object)