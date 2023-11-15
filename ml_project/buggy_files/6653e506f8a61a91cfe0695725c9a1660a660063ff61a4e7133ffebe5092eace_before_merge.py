    def parse_pubdate(pubdate, human_time=False, timezone=None, **kwargs):
        """
        Parse publishing date into a datetime object.

        :param pubdate: date and time string
        :param human_time: string uses human slang ("4 hours ago")
        :param timezone: use a different timezone ("US/Eastern")

        :keyword dayfirst: Interpret the first value as the day
        :keyword yearfirst: Interpret the first value as the year

        :returns: a datetime object or None
        """
        now_alias = ('right now', 'just now', 'now')

        df = kwargs.pop('dayfirst', False)
        yf = kwargs.pop('yearfirst', False)
        fromtimestamp = kwargs.pop('fromtimestamp', False)

        # This can happen from time to time
        if pubdate is None:
            log.debug('Skipping invalid publishing date.')
            return

        try:
            if human_time:
                if pubdate.lower() in now_alias:
                    seconds = 0
                else:
                    match = re.search(r'(?P<time>[\d.]+\W*)(?P<granularity>\w+)', pubdate)
                    matched_time = match.group('time')
                    matched_granularity = match.group('granularity')

                    # The parse method does not support decimals used with the month,
                    # months, year or years granularities.
                    if matched_granularity and matched_granularity in ('month', 'months', 'year', 'years'):
                        matched_time = int(round(float(matched_time.strip())))

                    seconds = parse('{0} {1}'.format(matched_time, matched_granularity))
                return datetime.now(tz.tzlocal()) - timedelta(seconds=seconds)

            if fromtimestamp:
                dt = datetime.fromtimestamp(int(pubdate), tz=tz.gettz('UTC'))
            else:
                dt = parser.parse(pubdate, dayfirst=df, yearfirst=yf, fuzzy=True)

            # Always make UTC aware if naive
            if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
                dt = dt.replace(tzinfo=tz.gettz('UTC'))
            if timezone:
                dt = dt.astimezone(tz.gettz(timezone))

            return dt
        except (AttributeError, TypeError, ValueError):
            log.exception('Failed parsing publishing date: {0}', pubdate)