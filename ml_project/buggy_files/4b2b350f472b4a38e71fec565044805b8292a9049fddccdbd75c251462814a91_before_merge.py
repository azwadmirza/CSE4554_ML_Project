  def PrintLine(self):
    """"Return a string with combined values from the lexer."""
    year = getattr(self.attributes, 'iyear', None)
    month = getattr(self.attributes, 'imonth', None)
    day = getattr(self.attributes, 'iday', None)

    if None in [year, month, day]:
      date_string = u'[DATE NOT SET]'
    else:
      try:
        year = int(year, 10)
        month = int(month, 10)
        day = int(day, 10)

        date_string = u'{0:04d}-{1:02d}-{2:02d}'.format(year, month, day)
      except ValueError:
        date_string = u'[DATE INVALID]'

    time_string = getattr(self.attributes, 'time', u'[TIME NOT SET]')
    hostname_string = getattr(self.attributes, 'hostname', u'HOSTNAME NOT SET')
    reporter_string = getattr(
        self.attributes, 'reporter', u'[REPORTER NOT SET]')
    body_string = getattr(self.attributes, 'body', u'[BODY NOT SET]')

    # TODO: this is a work in progress. The reason for the try-catch is that
    # the text parser is handed a non-text file and must deal with converting
    # arbitrary binary data.
    try:
      line = u'{0:s} {1:s} [{2:s}] {3:s} => {4:s}'.format(
          date_string, time_string, hostname_string, reporter_string,
          body_string)
    except UnicodeError:
      line = 'Unable to print line - due to encoding error.'

    return line