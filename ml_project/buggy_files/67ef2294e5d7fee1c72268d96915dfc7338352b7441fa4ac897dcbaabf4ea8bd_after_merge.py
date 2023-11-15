    def _build_datetime(parts):

        weekdate = parts.get("weekdate")

        if weekdate is not None:
            # we can use strptime (%G, %V, %u) in python 3.6 but these tokens aren't available before that
            year, week = int(weekdate[0]), int(weekdate[1])

            if weekdate[2] is not None:
                day = int(weekdate[2])
            else:
                # day not given, default to 1
                day = 1

            dt = iso_to_gregorian(year, week, day)
            parts["year"] = dt.year
            parts["month"] = dt.month
            parts["day"] = dt.day

        timestamp = parts.get("timestamp")

        if timestamp is not None:
            return datetime.fromtimestamp(timestamp, tz=tz.tzutc())

        expanded_timestamp = parts.get("expanded_timestamp")

        if expanded_timestamp is not None:
            return datetime.fromtimestamp(
                normalize_timestamp(expanded_timestamp), tz=tz.tzutc(),
            )

        day_of_year = parts.get("day_of_year")

        if day_of_year is not None:
            year = parts.get("year")
            month = parts.get("month")
            if year is None:
                raise ParserError(
                    "Year component is required with the DDD and DDDD tokens."
                )

            if month is not None:
                raise ParserError(
                    "Month component is not allowed with the DDD and DDDD tokens."
                )

            date_string = "{}-{}".format(year, day_of_year)
            try:
                dt = datetime.strptime(date_string, "%Y-%j")
            except ValueError:
                raise ParserError(
                    "The provided day of year '{}' is invalid.".format(day_of_year)
                )

            parts["year"] = dt.year
            parts["month"] = dt.month
            parts["day"] = dt.day

        am_pm = parts.get("am_pm")
        hour = parts.get("hour", 0)

        if am_pm == "pm" and hour < 12:
            hour += 12
        elif am_pm == "am" and hour == 12:
            hour = 0

        # Support for midnight at the end of day
        if hour == 24:
            if parts.get("minute", 0) != 0:
                raise ParserError("Midnight at the end of day must not contain minutes")
            if parts.get("second", 0) != 0:
                raise ParserError("Midnight at the end of day must not contain seconds")
            if parts.get("microsecond", 0) != 0:
                raise ParserError(
                    "Midnight at the end of day must not contain microseconds"
                )
            hour = 0
            day_increment = 1
        else:
            day_increment = 0

        # account for rounding up to 1000000
        microsecond = parts.get("microsecond", 0)
        if microsecond == 1000000:
            microsecond = 0
            second_increment = 1
        else:
            second_increment = 0

        increment = timedelta(days=day_increment, seconds=second_increment)

        return (
            datetime(
                year=parts.get("year", 1),
                month=parts.get("month", 1),
                day=parts.get("day", 1),
                hour=hour,
                minute=parts.get("minute", 0),
                second=parts.get("second", 0),
                microsecond=microsecond,
                tzinfo=parts.get("tzinfo"),
            )
            + increment
        )