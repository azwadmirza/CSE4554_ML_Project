    def _getDateTime(self):
        """
        Returns a Python datetime object.

        :rtype: :class:`datetime.datetime`
        :return: Python datetime object.

        .. rubric:: Example

        >>> dt = UTCDateTime(2008, 10, 1, 12, 30, 35, 45020)
        >>> dt.datetime
        datetime.datetime(2008, 10, 1, 12, 30, 35, 45020)
        """
        # we are exact at the border of floating point precision
        # datetime.utcfromtimestamp will cut off but not round
        # avoid through adding extra timedelta
        _fsec, _isec = math.modf(self.timestamp)
        return datetime.datetime.utcfromtimestamp(_isec) + \
            datetime.timedelta(seconds=_fsec)