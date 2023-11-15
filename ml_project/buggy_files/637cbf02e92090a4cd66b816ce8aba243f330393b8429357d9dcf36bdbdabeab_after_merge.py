    def _from_arraylike(cls, data, freq):
        if not isinstance(data, np.ndarray):
            if np.isscalar(data) or isinstance(data, Period):
                raise ValueError('PeriodIndex() must be called with a '
                                 'collection of some kind, %s was passed'
                                 % repr(data))

            # other iterable of some kind
            if not isinstance(data, (list, tuple)):
                data = list(data)

            try:
                data = com._ensure_int64(data)
                if freq is None:
                    raise ValueError('freq not specified')
                data = np.array([Period(x, freq=freq).ordinal for x in data],
                                dtype=np.int64)
            except (TypeError, ValueError):
                data = com._ensure_object(data)

                if freq is None and len(data) > 0:
                    freq = getattr(data[0], 'freq', None)

                if freq is None:
                    raise ValueError('freq not specified and cannot be '
                                     'inferred from first element')

                data = _get_ordinals(data, freq)
        else:
            if isinstance(data, PeriodIndex):
                if freq is None or freq == data.freq:
                    freq = data.freq
                    data = data.values
                else:
                    base1, _ = _gfc(data.freq)
                    base2, _ = _gfc(freq)
                    data = plib.period_asfreq_arr(data.values, base1, base2, 1)
            else:
                if freq is None and len(data) > 0:
                    freq = getattr(data[0], 'freq', None)

                if freq is None:
                    raise ValueError(('freq not specified and cannot be '
                                      'inferred from first element'))

                if np.issubdtype(data.dtype, np.datetime64):
                    data = dt64arr_to_periodarr(data, freq)
                elif data.dtype == np.int64:
                    pass
                else:
                    try:
                        data = com._ensure_int64(data)
                    except (TypeError, ValueError):
                        data = com._ensure_object(data)
                        data = _get_ordinals(data, freq)

        return data, freq