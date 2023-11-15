    def __new__(cls, data=None,
                freq=None, start=None, end=None, periods=None,
                dtype=None, copy=False, name=None, tz=None,
                verify_integrity=True, normalize=False, **kwds):

        warn = False
        if 'offset' in kwds and kwds['offset']:
            freq = kwds['offset']
            warn = True

        if not isinstance(freq, datetools.DateOffset):
            freq = datetools.to_offset(freq)

        if warn:
            import warnings
            warnings.warn("parameter 'offset' is deprecated, "
                          "please use 'freq' instead",
                          FutureWarning)
            if isinstance(freq, basestring):
                freq = datetools.get_offset(freq)
        else:
            if isinstance(freq, basestring):
                freq = datetools.to_offset(freq)

        offset = freq

        if data is None and offset is None:
            raise ValueError("Must provide freq argument if no data is "
                             "supplied")

        if data is None:
            _normalized = True

            if start is not None:
                start = Timestamp(start)
                if not isinstance(start, Timestamp):
                    raise ValueError('Failed to convert %s to timestamp'
                                     % start)

                if normalize:
                    start = datetools.normalize_date(start)
                    _normalized = True
                else:
                    _normalized = _normalized and start.time() == _midnight

            if end is not None:
                end = Timestamp(end)
                if not isinstance(end, Timestamp):
                    raise ValueError('Failed to convert %s to timestamp'
                                     % end)

                if normalize:
                    end = datetools.normalize_date(end)
                    _normalized = True
                else:
                    _normalized = _normalized and end.time() == _midnight

            start, end, tz = tools._figure_out_timezone(start, end, tz)

            if (offset._should_cache() and
                not (offset._normalize_cache and not _normalized) and
                datetools._naive_in_cache_range(start, end)):
                index = cls._cached_range(start, end, periods=periods,
                                          offset=offset, name=name)
            else:
                if isinstance(offset, datetools.Tick):
                    if periods is None:
                        b, e = Timestamp(start), Timestamp(end)
                        data = np.arange(b.value, e.value+1,
                                        offset.us_stride(), dtype=np.int64)
                    else:
                        b = Timestamp(start)
                        e = b.value + periods * offset.us_stride()
                        data = np.arange(b.value, e,
                                         offset.us_stride(), dtype=np.int64)

                else:
                    xdr = datetools.generate_range(start=start, end=end,
                        periods=periods, offset=offset)

                    data = _to_m8_array(list(xdr))

                index = np.array(data, dtype=np.datetime64, copy=False)

            index = index.view(cls)
            index.name = name
            index.offset = offset
            index.tz = tz

            return index

        if not isinstance(data, np.ndarray):
            if np.isscalar(data):
                raise ValueError('DatetimeIndex() must be called with a '
                                 'collection of some kind, %s was passed'
                                 % repr(data))

            if isinstance(data, datetime):
                data = [data]

            # other iterable of some kind
            if not isinstance(data, (list, tuple)):
                data = list(data)

            data = np.asarray(data, dtype='O')

            # try a few ways to make it datetime64
            if lib.is_string_array(data):
                data = _str_to_dt_array(data)
            else:
                data = np.asarray(data, dtype='M8[us]')

        if issubclass(data.dtype.type, basestring):
            subarr = _str_to_dt_array(data)
        elif issubclass(data.dtype.type, np.integer):
            subarr = np.array(data, dtype='M8[us]', copy=copy)
        elif issubclass(data.dtype.type, np.datetime64):
            subarr = np.array(data, dtype='M8[us]', copy=copy)
        else:
            subarr = np.array(data, dtype='M8[us]', copy=copy)

        # TODO: this is horribly inefficient. If user passes data + offset, we
        # need to make sure data points conform. Punting on this

        if verify_integrity:
            if offset is not None:
                for i, ts in enumerate(subarr):
                    if not offset.onOffset(Timestamp(ts)):
                        val = Timestamp(offset.rollforward(ts)).value
                        subarr[i] = val

        subarr = subarr.view(cls)
        subarr.name = name
        subarr.offset = offset
        subarr.tz = tz

        return subarr