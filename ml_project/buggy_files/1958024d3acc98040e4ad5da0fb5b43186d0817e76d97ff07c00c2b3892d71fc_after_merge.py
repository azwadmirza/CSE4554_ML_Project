    def __init__(self, granularity=None, points=None, timespan=None):
        if (granularity is not None
           and points is not None
           and timespan is not None):
            if timespan != granularity * points:
                raise ValueError(
                    u"timespan ≠ granularity × points")

        if granularity is not None and granularity <= 0:
            raise ValueError("Granularity should be > 0")

        if points is not None and points <= 0:
            raise ValueError("Number of points should be > 0")

        if granularity is None:
            if points is None or timespan is None:
                raise ValueError(
                    "At least two of granularity/points/timespan "
                    "must be provided")
            granularity = round(timespan / float(points))
        else:
            granularity = float(granularity)

        if points is None:
            if timespan is None:
                self['timespan'] = None
            else:
                points = int(timespan / granularity)
                if points <= 0:
                    raise ValueError("Calculated number of points is < 0")
                self['timespan'] = granularity * points
        else:
            points = int(points)
            self['timespan'] = granularity * points

        self['points'] = points
        self['granularity'] = granularity