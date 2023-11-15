def guessrangefstr(daterange, locale, default_timedelta=None, adjust_reasonably=False):
    """parses a range string

    :param daterange: date1 [date2 | timedelta]
    :type daterange: str or list
    :param locale:
    :rtype: (datetime, datetime, bool)

    """
    range_list = daterange
    if isinstance(daterange, str):
        range_list = daterange.split(' ')

    try:
        if default_timedelta is None or len(default_timedelta) == 0:
            default_timedelta = None
        else:
            default_timedelta = guesstimedeltafstr(default_timedelta)
    except ValueError:
        default_timedelta = None

    for i in reversed(range(1, len(range_list) + 1)):
        start = ' '.join(range_list[:i])
        end = ' '.join(range_list[i:])
        allday = False
        try:
            # figuring out start
            if len(start) == 0:
                start = datetime_fillin(end=False)
            elif start.lower() == 'week':
                    today_weekday = datetime.today().weekday()
                    start = datetime.today() - \
                        timedelta(days=(today_weekday - locale['firstweekday']))
                    end = start + timedelta(days=7)
            else:
                split = start.split(" ")
                start, allday = guessdatetimefstr(split, locale)
                if len(split) != 0:
                    continue

            # and end
            if len(end) == 0:
                if default_timedelta is not None:
                    end = start + default_timedelta
                else:
                    end = datetime_fillin(day=start)
            elif end.lower() == 'eod':
                    end = datetime_fillin(day=start)
            elif end.lower() == 'week':
                start -= timedelta(days=(start.weekday() - locale['firstweekday']))
                end = start + timedelta(days=7)
            else:

                try:
                    delta = guesstimedeltafstr(end)
                    end = start + delta
                except ValueError:
                    split = end.split(" ")
                    end, end_allday = guessdatetimefstr(split, locale, default_day=start.date())
                    if len(split) != 0:
                        continue
                end = datetime_fillin(end)

            if adjust_reasonably:
                if allday:
                    # TODO move out of here, this is an icalendar peculiarity
                    end += timedelta(days=1)
                    # test if end's year is this year, but start's year is not
                    today = datetime.today()
                    if end.year == today.year and start.year != today.year:
                        end = datetime(start.year, *end.timetuple()[1:6])

                    if end < start:
                        end = datetime(end.year + 1, *end.timetuple()[1:6])

                if end < start:
                    end = datetime(*start.timetuple()[0:3] + end.timetuple()[3:5])
                if end < start:
                    end = end + timedelta(days=1)
            return start, end, allday
        except ValueError:
            pass

    raise ValueError('Could not parse `{}` as a daterange'.format(daterange))