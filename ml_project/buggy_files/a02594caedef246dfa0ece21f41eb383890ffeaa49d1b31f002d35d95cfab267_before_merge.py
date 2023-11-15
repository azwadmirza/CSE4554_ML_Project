    def __call__(self, *args, **kwargs):
        """ Method for running the factory. Takes arbitrary arguments and
        keyword arguments and passes them to a sequence of pre-registered types
        to determine which is the correct TimeSeries source type to build.

        Arguments args and kwargs are passed through to the validation
        function and to the constructor for the final type.  For TimeSeries
        types, validation function must take a data-header pair as an argument.

        Parameters
        ----------

        silence_errors : `bool`, optional
            If set, ignore data-header pairs which cause an exception.

        Notes
        -----
        Extra keyword arguments are passed through to `sunpy.io.read_file` such
        as `memmap` for FITS files.
        """

        # Hack to get around Python 2.x not backporting PEP 3102.
        silence_errors = kwargs.pop('silence_errors', False)

        (data_header_unit_tuples, data_header_pairs,
         already_timeseries, filepaths) = self._parse_args(*args, **kwargs)

        new_timeseries = list()

        # The filepaths for unreadable files
        for filepath in filepaths:
            try:
                new_ts = self._check_registered_widgets(filepath=filepath, **kwargs)
            except (NoMatchError, MultipleMatchError, ValidationFunctionError):
                if not silence_errors:
                    raise
            except Exception:
                raise

            new_timeseries.append(new_ts)

        # data_header_pairs is a list of HDUs as read by sunpy.io
        # For each set of HDus find the matching class and read the
        # data_header_unit_tuples by calling the _parse_hdus method
        # of the class.
        for pairs in data_header_pairs:
            # Pairs may be x long where x is the number of HDUs in the file.
            headers = [pair.header for pair in pairs]

            types = []
            for header in headers:
                try:
                    match = self._get_matching_widget(meta=header, **kwargs)
                    if not match == GenericTimeSeries:
                        types.append(match)
                except (MultipleMatchError, NoMatchError):
                    continue

            if not types:
                # If no specific classes have been found we can read the data
                # if we only have one data header pair:
                if len(pairs) == 1:
                    already_timeseries.append(GenericTimeSeries(pairs[0].data,
                                                                pairs[0].header))
                else:
                    raise NoMatchError("Input read by sunpy.io can not find a "
                                       "matching class for reading multiple HDUs")
            if len(set(types)) > 1:
                raise MultipleMatchError("Multiple HDUs return multiple matching classes.")

            cls = types[0]

            data_header_unit_tuples.append(cls._parse_hdus(pairs))

        # Loop over each registered type and check to see if WidgetType
        # matches the arguments.  If it does, use that type
        for triple in data_header_unit_tuples:
            data, header, units = triple
            # Make a MetaDict from various input types
            meta = header
            if isinstance(meta, astropy.io.fits.header.Header):
                meta = sunpy.io.header.FileHeader(meta)
            meta = MetaDict(meta)

            try:
                new_ts = self._check_registered_widgets(data=data, meta=meta,
                                                        units=units, **kwargs)
            except (NoMatchError, MultipleMatchError, ValidationFunctionError):
                if not silence_errors:
                    raise
            except Exception:
                raise

            new_timeseries.append(new_ts)

        new_timeseries += already_timeseries

        # Concatenate the timeseries into one if specified.
        concatenate = kwargs.get('concatenate', False)
        if concatenate:
            # Merge all these timeseries into one.
            full_timeseries = new_timeseries.pop(0)
            for timeseries in new_timeseries:
                full_timeseries = full_timeseries.concatenate(timeseries)

            new_timeseries = [full_timeseries]

        # Sanitize any units OrderedDict details
        for timeseries in new_timeseries:
            timeseries._sanitize_units()

        # Only return single time series, not in a list if we only have one.
        if len(new_timeseries) == 1:
            return new_timeseries[0]
        return new_timeseries