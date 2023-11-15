    def setup(self):
        self.ts = Timestamp('2017-08-25 08:16:14')
        self.ts_tz = Timestamp('2017-08-25 08:16:14', tz='US/Eastern')

        dt = datetime.datetime(2016, 3, 27, 1)
        self.tzinfo = pytz.timezone('CET').localize(dt, is_dst=False).tzinfo
        self.ts2 = Timestamp(dt)