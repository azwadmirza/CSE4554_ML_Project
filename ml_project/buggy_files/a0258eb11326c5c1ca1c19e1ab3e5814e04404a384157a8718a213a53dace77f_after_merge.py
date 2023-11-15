    def fromtimestamp(cls, timestamp, tzinfo=None):
        """ Constructs an :class:`Arrow <arrow.arrow.Arrow>` object from a timestamp, converted to
        the given timezone.

        :param timestamp: an ``int`` or ``float`` timestamp, or a ``str`` that converts to either.
        :param tzinfo: (optional) a ``tzinfo`` object.  Defaults to local time.
        """

        if tzinfo is None:
            tzinfo = dateutil_tz.tzlocal()
        elif util.isstr(tzinfo):
            tzinfo = parser.TzinfoParser.parse(tzinfo)

        if not util.is_timestamp(timestamp):
            raise ValueError(
                "The provided timestamp '{}' is invalid.".format(timestamp)
            )

        timestamp = util.normalize_timestamp(float(timestamp))
        dt = datetime.fromtimestamp(timestamp, tzinfo)

        return cls(
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second,
            dt.microsecond,
            dt.tzinfo,
        )