    def __new__(cls, data=None,
                freq=None, start=None, end=None, periods=None,
                copy=False, name=None, tz=None,
                verify_integrity=True, normalize=False, **kwds):

        warn = False
        if 'offset' in kwds and kwds['offset']:
            freq = kwds['offset']
            warn = True

        infer_freq = False
        if not isinstance(freq, DateOffset):
            if freq != 'infer':
                freq = to_offset(freq)
            else:
                infer_freq = True
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
                data = _str_to_dt_array(data, offset)
            else:
                data = tools.to_datetime(data)
                data.offset = offset

        if issubclass(data.dtype.type, basestring):
            subarr = _str_to_dt_array(data, offset)
        elif issubclass(data.dtype.type, np.datetime64):
            if isinstance(data, DatetimeIndex):
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
            subarr = np.asarray(data, dtype=_NS_DTYPE)
        else:
            subarr = tools.to_datetime(data)
            if not np.issubdtype(subarr.dtype, np.datetime64):
                raise TypeError('Unable to convert %s to datetime dtype'
                                % str(data))

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
            if offset is not None and not infer_freq:
                inferred = subarr.inferred_freq
                if inferred != offset.freqstr:
                    raise ValueError('Dates do not conform to passed '
                                     'frequency')

        if infer_freq:
            inferred = subarr.inferred_freq
            if inferred:
                subarr.offset = to_offset(inferred)

        return subarr