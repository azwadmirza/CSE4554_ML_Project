    def humanize(
        self, other=None, locale="en_us", only_distance=False, granularity="auto"
    ):
        """ Returns a localized, humanized representation of a relative difference in time.

        :param other: (optional) an :class:`Arrow <arrow.arrow.Arrow>` or ``datetime`` object.
            Defaults to now in the current :class:`Arrow <arrow.arrow.Arrow>` object's timezone.
        :param locale: (optional) a ``str`` specifying a locale.  Defaults to 'en_us'.
        :param only_distance: (optional) returns only time difference eg: "11 seconds" without "in" or "ago" part.
        :param granularity: (optional) defines the precision of the output. Set it to strings 'second', 'minute', 'hour', 'day', 'month' or 'year'.

        Usage::

            >>> earlier = arrow.utcnow().shift(hours=-2)
            >>> earlier.humanize()
            '2 hours ago'

            >>> later = earlier.shift(hours=4)
            >>> later.humanize(earlier)
            'in 4 hours'

        """

        locale = locales.get_locale(locale)

        if other is None:
            utc = datetime.utcnow().replace(tzinfo=dateutil_tz.tzutc())
            dt = utc.astimezone(self._datetime.tzinfo)

        elif isinstance(other, Arrow):
            dt = other._datetime

        elif isinstance(other, datetime):
            if other.tzinfo is None:
                dt = other.replace(tzinfo=self._datetime.tzinfo)
            else:
                dt = other.astimezone(self._datetime.tzinfo)

        else:
            raise TypeError()

        delta = int(round(util.total_seconds(self._datetime - dt)))
        sign = -1 if delta < 0 else 1
        diff = abs(delta)
        delta = diff

        if granularity == "auto":
            if diff < 10:
                return locale.describe("now", only_distance=only_distance)

            if diff < 45:
                seconds = sign * delta
                return locale.describe("seconds", seconds, only_distance=only_distance)

            elif diff < 90:
                return locale.describe("minute", sign, only_distance=only_distance)
            elif diff < 2700:
                minutes = sign * int(max(delta / 60, 2))
                return locale.describe("minutes", minutes, only_distance=only_distance)

            elif diff < 5400:
                return locale.describe("hour", sign, only_distance=only_distance)
            elif diff < 79200:
                hours = sign * int(max(delta / 3600, 2))
                return locale.describe("hours", hours, only_distance=only_distance)

            elif diff < 129600:
                return locale.describe("day", sign, only_distance=only_distance)
            elif diff < 554400:
                days = sign * int(max(delta / 86400, 2))
                return locale.describe("days", days, only_distance=only_distance)

            elif diff < 907200:
                return locale.describe("week", sign, only_distance=only_distance)
            elif diff < 2419200:
                weeks = sign * int(max(delta / 604800, 2))
                return locale.describe("weeks", weeks, only_distance=only_distance)

            elif diff < 3888000:
                return locale.describe("month", sign, only_distance=only_distance)
            elif diff < 29808000:
                self_months = self._datetime.year * 12 + self._datetime.month
                other_months = dt.year * 12 + dt.month

                months = sign * int(max(abs(other_months - self_months), 2))

                return locale.describe("months", months, only_distance=only_distance)

            elif diff < 47260800:
                return locale.describe("year", sign, only_distance=only_distance)
            else:
                years = sign * int(max(delta / 31536000, 2))
                return locale.describe("years", years, only_distance=only_distance)

        else:
            if granularity == "second":
                delta = sign * delta
                if abs(delta) < 2:
                    return locale.describe("now", only_distance=only_distance)
            elif granularity == "minute":
                delta = sign * delta / float(60)
            elif granularity == "hour":
                delta = sign * delta / float(60 * 60)
            elif granularity == "day":
                delta = sign * delta / float(60 * 60 * 24)
            elif granularity == "week":
                delta = sign * delta / float(60 * 60 * 24 * 7)
            elif granularity == "month":
                delta = sign * delta / float(60 * 60 * 24 * 30.5)
            elif granularity == "year":
                delta = sign * delta / float(60 * 60 * 24 * 365.25)
            else:
                raise AttributeError(
                    'Error. Could not understand your level of granularity. Please select between \
                "second", "minute", "hour", "day", "week", "month" or "year"'
                )

            if trunc(abs(delta)) != 1:
                granularity += "s"
            return locale.describe(granularity, delta, only_distance=only_distance)