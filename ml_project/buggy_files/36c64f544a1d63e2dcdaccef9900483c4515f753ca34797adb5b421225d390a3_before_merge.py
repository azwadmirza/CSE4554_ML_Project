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
        return datetime.datetime.utcfromtimestamp(self.timestamp)