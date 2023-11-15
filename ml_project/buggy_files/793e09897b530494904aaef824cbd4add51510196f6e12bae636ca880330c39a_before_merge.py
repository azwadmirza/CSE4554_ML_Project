    def __new__(cls, data=None,
                freq=None, start=None, end=None, periods=None,
                copy=False, name=None, tz=None,
                verify_integrity=True, normalize=False, **kwds):

        dayfirst = kwds.pop('dayfirst', None)
        yearfirst = kwds.pop('yearfirst', None)
        warn = False
        if 'offset' in kwds and kwds['offset']:
            freq = kwds['offset']
            warn = True

        freq_infer = False
        if not isinstance(freq, DateOffset):
            if freq != 'infer':
                freq = to_offset(freq)
            else:
                freq_infer = True
                freq = None

        if warn:
            import warnings
            warnings.warn("parameter 'offset' is deprecated, "
                          "please use 'freq' instead",
                          FutureWarning)

        offset = freq

        if periods is not None:
            if com.is_float(periods):
                periods = int(periods)
            elif not com.is_integer(periods):
                raise ValueError('Periods must be a number, got %s' %
                                 str(periods))

        if data is None and offset is None:
            raise ValueError("Must provide freq argument if no data is "
                             "supplied")

        if data is None:
            return cls._generate(start, end, periods, name, offset,
                                 tz=tz, normalize=normalize)

        if not isinstance(data, np.ndarray):
            if np.isscalar(data):
                raise ValueError('DatetimeIndex() must be called with a '
                                 'collection of some kind, %s was passed'
                                 % repr(data))

            # other iterable of some kind
            if not isinstance(data, (list, tuple)):
                data = list(data)

            data = np.asarray(data, dtype='O')

            # try a few ways to make it datetime64
            if lib.is_string_array(data):
                data = _str_to_dt_array(data, offset, dayfirst=dayfirst,
                                        yearfirst=yearfirst)
            else:
                data = tools.to_datetime(data)
                data.offset = offset
                if isinstance(data, DatetimeIndex):
                    if name is not None:
                        data.name = name
                    return data

        if issubclass(data.dtype.type, basestring):
            subarr = _str_to_dt_array(data, offset, dayfirst=dayfirst,
                                      yearfirst=yearfirst)
        elif issubclass(data.dtype.type, np.datetime64):
            if isinstance(data, DatetimeIndex):
                if tz is None:
                    tz = data.tz

                subarr = data.values

                if offset is None:
                    offset = data.offset
                    verify_integrity = False
            else:
                if data.dtype != _NS_DTYPE:
                    subarr = lib.cast_to_nanoseconds(data)
                else:
                    subarr = data
        elif data.dtype == _INT64_DTYPE:
            if copy:
                subarr = np.asarray(data, dtype=_NS_DTYPE)
            else:
                subarr = data.view(_NS_DTYPE)
        else:
            try:
                subarr = tools.to_datetime(data)
            except ValueError:
                # tz aware
                subarr = tools.to_datetime(data, utc=True)

            if not np.issubdtype(subarr.dtype, np.datetime64):
                raise TypeError('Unable to convert %s to datetime dtype'
                                % str(data))

        if isinstance(subarr, DatetimeIndex):
            if tz is None:
                tz = subarr.tz
        else:
            if tz is not None:
                tz = tools._maybe_get_tz(tz)
                # Convert local to UTC
                ints = subarr.view('i8')

                subarr = lib.tz_localize_to_utc(ints, tz)
                subarr = subarr.view(_NS_DTYPE)

        subarr = subarr.view(cls)
        subarr.name = name
        subarr.offset = offset
        subarr.tz = tz

        if verify_integrity and len(subarr) > 0:
            if offset is not None and not freq_infer:
                inferred = subarr.inferred_freq
                if inferred != offset.freqstr:
                    raise ValueError('Dates do not conform to passed '
                                     'frequency')

        if freq_infer:
            inferred = subarr.inferred_freq
            if inferred:
                subarr.offset = to_offset(inferred)

        return subarr