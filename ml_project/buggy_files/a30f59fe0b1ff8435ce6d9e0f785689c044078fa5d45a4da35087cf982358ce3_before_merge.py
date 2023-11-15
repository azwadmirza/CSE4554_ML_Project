def vertical_month(month=datetime.date.today().month,
                   year=datetime.date.today().year,
                   today=datetime.date.today(),
                   weeknumber=False,
                   count=3,
                   firstweekday=0):
    """
    returns a list() of str() of weeks for a vertical arranged calendar

    :param month: first month of the calendar,
                  if non given, current month is assumed
    :type month: int
    :param year: year of the first month included,
                 if non given, current year is assumed
    :type year: int
    :param today: day highlighted, if non is given, current date is assumed
    :type today: datetime.date()
    :param weeknumber: if not False the iso weeknumber will be shown for each
                       week, if weeknumber is 'right' it will be shown in its
                       own column, if it is 'left' it will be shown interleaved
                       with the month names
    :type weeknumber: str/bool
    :returns: calendar strings,  may also include some
              ANSI (color) escape strings
    :rtype: list() of str()
    """

    khal = list()
    w_number = '    ' if weeknumber == 'right' else ''
    calendar.setfirstweekday(firstweekday)
    _calendar = calendar.Calendar(firstweekday)
    khal.append(bstring('    ' + calendar.weekheader(2) + ' ' + w_number))
    for _ in range(count):
        for week in _calendar.monthdatescalendar(year, month):
            new_month = len([day for day in week if day.day == 1])
            strweek = str_week(week, today)
            if new_month:
                m_name = bstring(calendar.month_abbr[week[6].month].ljust(4))
            elif weeknumber == 'left':
                m_name = bstring(' {:2} '.format(getweeknumber(week[0])))
            else:
                m_name = '    '
            if weeknumber == 'right':
                w_number = bstring(' {}'.format(getweeknumber(week[0])))
            else:
                w_number = ''

            sweek = m_name + strweek + w_number
            if sweek != khal[-1]:
                khal.append(sweek)
        month = month + 1
        if month > 12:
            month = 1
            year = year + 1
    return khal