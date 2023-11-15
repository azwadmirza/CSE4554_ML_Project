    def utcfromtimestamp(cls, timestamp):
        """Constructs an :class:`Arrow <arrow.arrow.Arrow>` object from a timestamp, in UTC time.

        :param timestamp: an ``int`` or ``float`` timestamp, or a ``str`` that converts to either.

        """

        if not util.is_timestamp(timestamp):
            raise ValueError(
                "The provided timestamp '{}' is invalid.".format(timestamp)
            )

        timestamp = util.normalize_timestamp(float(timestamp))
        dt = datetime.utcfromtimestamp(timestamp)

        return cls(
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second,
            dt.microsecond,
            dateutil_tz.tzutc(),
        )