    def setup(self, orient, frame):
        N = 10 ** 5
        ncols = 5
        index = date_range("20000101", periods=N, freq="H")
        timedeltas = timedelta_range(start=1, periods=N, freq="s")
        datetimes = date_range(start=1, periods=N, freq="s")
        ints = np.random.randint(100000000, size=N)
        floats = np.random.randn(N)
        strings = tm.makeStringIndex(N)
        self.df = DataFrame(np.random.randn(N, ncols), index=np.arange(N))
        self.df_date_idx = DataFrame(np.random.randn(N, ncols), index=index)
        self.df_td_int_ts = DataFrame(
            {
                "td_1": timedeltas,
                "td_2": timedeltas,
                "int_1": ints,
                "int_2": ints,
                "ts_1": datetimes,
                "ts_2": datetimes,
            },
            index=index,
        )
        self.df_int_floats = DataFrame(
            {
                "int_1": ints,
                "int_2": ints,
                "int_3": ints,
                "float_1": floats,
                "float_2": floats,
                "float_3": floats,
            },
            index=index,
        )
        self.df_int_float_str = DataFrame(
            {
                "int_1": ints,
                "int_2": ints,
                "float_1": floats,
                "float_2": floats,
                "str_1": strings,
                "str_2": strings,
            },
            index=index,
        )