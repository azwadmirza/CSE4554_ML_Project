    def group_serie(self, granularity, start=None):
        # NOTE(jd) Our whole serialization system is based on Epoch, and we
        # store unsigned integer, so we can't store anything before Epoch.
        # Sorry!
        if not self.ts.empty and self.ts.index[0].value < 0:
            raise BeforeEpochError(self.ts.index[0])
        return self.ts[start:].groupby(functools.partial(
            round_timestamp, freq=granularity * 10e8))