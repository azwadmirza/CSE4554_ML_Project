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
        # datetime.utcfromtimestamp will cut off but not round
        # avoid through adding timedelta - also avoids the year 2038 problem
        return datetime.datetime.utcfromtimestamp(0) + \
            datetime.timedelta(seconds=self.timestamp)