    def group_serie(self, granularity, start=0):
        # NOTE(jd) Our whole serialization system is based on Epoch, and we
        # store unsigned integer, so we can't store anything before Epoch.
        # Sorry!
        if self.ts.index[0].value < 0:
            raise BeforeEpochError(self.ts.index[0])

        return GroupedTimeSeries(self.ts[start:], granularity)