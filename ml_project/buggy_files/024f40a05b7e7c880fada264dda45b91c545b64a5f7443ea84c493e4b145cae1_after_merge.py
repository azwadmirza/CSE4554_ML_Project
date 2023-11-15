    def _convert_listlike(arg, box, format, name=None):

        if isinstance(arg, (list, tuple)):
            arg = np.array(arg, dtype='O')

        # these are shortcutable
        if com.is_datetime64_ns_dtype(arg):
            if box and not isinstance(arg, DatetimeIndex):
                try:
                    return DatetimeIndex(arg, tz='utc' if utc else None,
                                         name=name)
                except ValueError:
                    pass

            return arg

        elif com.is_datetime64tz_dtype(arg):
            if not isinstance(arg, DatetimeIndex):
                return DatetimeIndex(arg, tz='utc' if utc else None)
            if utc:
                arg = arg.tz_convert(None)
            return arg

        elif format is None and com.is_integer_dtype(arg) and unit == 'ns':
            result = arg.astype('datetime64[ns]')
            if box:
                return DatetimeIndex(result, tz='utc' if utc else None,
                                     name=name)
            return result
        elif getattr(arg, 'ndim', 1) > 1:
            raise TypeError('arg must be a string, datetime, list, tuple, '
                            '1-d array, or Series')

        arg = com._ensure_object(arg)
        require_iso8601 = False

        if infer_datetime_format and format is None:
            format = _guess_datetime_format_for_array(arg, dayfirst=dayfirst)

        if format is not None:
            # There is a special fast-path for iso8601 formatted
            # datetime strings, so in those cases don't use the inferred
            # format because this path makes process slower in this
            # special case
            format_is_iso8601 = _format_is_iso(format)
            if format_is_iso8601:
                require_iso8601 = not infer_datetime_format
                format = None

        try:
            result = None

            if format is not None:
                # shortcut formatting here
                if format == '%Y%m%d':
                    try:
                        result = _attempt_YYYYMMDD(arg, errors=errors)
                    except:
                        raise ValueError("cannot convert the input to "
                                         "'%Y%m%d' date format")

                # fallback
                if result is None:
                    try:
                        result = tslib.array_strptime(
                            arg, format, exact=exact, errors=errors)
                    except tslib.OutOfBoundsDatetime:
                        if errors == 'raise':
                            raise
                        result = arg
                    except ValueError:
                        # if format was inferred, try falling back
                        # to array_to_datetime - terminate here
                        # for specified formats
                        if not infer_datetime_format:
                            if errors == 'raise':
                                raise
                            result = arg

            if result is None and (format is None or infer_datetime_format):
                result = tslib.array_to_datetime(
                    arg,
                    errors=errors,
                    utc=utc,
                    dayfirst=dayfirst,
                    yearfirst=yearfirst,
                    freq=freq,
                    unit=unit,
                    require_iso8601=require_iso8601
                )

            if com.is_datetime64_dtype(result) and box:
                result = DatetimeIndex(result,
                                       tz='utc' if utc else None,
                                       name=name)
            return result

        except ValueError as e:
            try:
                values, tz = tslib.datetime_to_datetime64(arg)
                return DatetimeIndex._simple_new(values, name=name, tz=tz)
            except (ValueError, TypeError):
                raise e