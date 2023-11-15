    def __new__(cls, data=None,
                freq=None, start=None, end=None, periods=None,
                copy=False, name=None):

        if isinstance(freq, Period):
            freq = freq.freq
        else:
            freq = _freq_mod.get_standard_freq(freq)

        if data is None:
            subarr, freq = _get_ordinal_range(start, end, periods, freq)
            subarr = subarr.view(cls)
            subarr.name = name
            subarr.freq = freq

            return subarr

        if not isinstance(data, np.ndarray):
            if np.isscalar(data):
                raise ValueError('PeriodIndex() must be called with a '
                                 'collection of some kind, %s was passed'
                                 % repr(data))

            elif isinstance(data, Period):
                raise ValueError('Data must be array of dates, strings, '
                                 'or Period objects')

            # other iterable of some kind
            if not isinstance(data, (list, tuple)):
                data = list(data)

            try:
                data = np.array(data, dtype='i8')
            except:
                data = np.array(data, dtype='O')

            if freq is None:
                raise ValueError('freq cannot be none')

            data = _period_unbox_array(data, check=freq)
        else:
            if isinstance(data, PeriodIndex):
                if freq is None or freq == data.freq:
                    freq = data.freq
                    data = data.values
                else:
                    base1, mult1 = _gfc(data.freq)
                    base2, mult2 = _gfc(freq)
                    data = lib.period_asfreq_arr(data.values, base1, mult1,
                                                 base2, mult2, b'E')
            else:
                if freq is None:
                    raise ValueError('freq cannot be none')

                if data.dtype == np.datetime64:
                    data = dt64arr_to_periodarr(data, freq)
                elif data.dtype == np.int64:
                    pass
                else:
                    data = data.astype('i8')

        data = np.array(data, dtype=np.int64, copy=False)

        if (data <= 0).any():
            raise ValueError("Found illegal (<= 0) values in data")

        subarr = data.view(cls)
        subarr.name = name
        subarr.freq = freq

        return subarr