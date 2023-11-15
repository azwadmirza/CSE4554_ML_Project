    def _parse_args(self, *args, **kwargs):
        """
        Parses an args list for data-header pairs.  args can contain any
        mixture of the following entries:
        * tuples of (data, header, unit) (1)
        * data, header not in a tuple (1)
        * filename, which will be read
        * directory, from which all files will be read
        * glob, from which all files will be read
        * url, which will be downloaded and read
        * lists containing any of the above.

        (1) Note that header/unit are optional and in either order, but data
        but be the first entry in each group.

        Example
        -------
        self._parse_args(data, header,
                         (data, header),
                         ['file1', 'file2', 'file3'],
                         'file4',
                         'directory1',
                         '*.fits')

        """

        data_header_unit_tuples = list()
        data_header_pairs = list()
        already_timeseries = list()
        filepaths = list()

        # Account for nested lists of items. Simply outputs a single list of
        # items, nested lists are expanded to element level.
        args = expand_list(args)

        # For each of the arguments, handle each of the cases
        i = 0
        while i < len(args):
            arg = args[i]

            # Data-header pair in a tuple
            if isinstance(arg, (np.ndarray, Table, pd.DataFrame)):
                # Assume a Pandas Dataframe is given
                data = arg
                units = OrderedDict()
                meta = MetaDict()

                # Convert the data argument into a Pandas DataFrame if needed.
                if isinstance(data, Table):
                    # We have an Astropy Table:
                    data, meta, units = self._from_table(data)
                elif isinstance(data, np.ndarray):
                    # We have a numpy ndarray. We assume the first column is a dt index
                    data = pd.DataFrame(data=data[:, 1:], index=Time(data[:, 0]))

                # If there are 1 or 2 more arguments:
                for _ in range(2):
                    if len(args) > i+1:
                        # If that next argument isn't data but is metaddata or units:
                        if not isinstance(args[i+1], (np.ndarray, Table, pd.DataFrame)):
                            if self._validate_units(args[i+1]):
                                units.update(args[i+1])
                                i += 1  # an extra increment to account for the units
                            elif self._validate_meta(args[i+1]):
                                # if we have an astropy.io FITS header then convert
                                # to preserve multi-line comments
                                if isinstance(args[i+1], astropy.io.fits.header.Header):
                                    args[i+1] = MetaDict(sunpy.io.header.FileHeader(args[i+1]))
                                meta.update(args[i+1])
                                i += 1  # an extra increment to account for the meta

                # Add a 3-tuple for this TimeSeries.
                data_header_unit_tuples.append((data, meta, units))

            # Filepath
            elif (isinstance(arg, str) and
                  os.path.isfile(os.path.expanduser(arg))):

                path = os.path.expanduser(arg)
                result = self._read_file(path, **kwargs)
                data_header_pairs, filepaths = _apply_result(data_header_pairs, filepaths, result)

            # Directory
            elif (isinstance(arg, str) and
                  os.path.isdir(os.path.expanduser(arg))):

                path = os.path.expanduser(arg)
                files = [os.path.join(path, elem) for elem in os.listdir(path)]
                for afile in files:
                    # returns a boolean telling us if it were read and either a
                    # tuple or the original filepath for reading by a source
                    result = self._read_file(afile, **kwargs)
                    data_header_pairs, filepaths = _apply_result(data_header_pairs, filepaths,
                                                                 result)

            # Glob
            elif isinstance(arg, str) and '*' in arg:

                files = glob.glob(os.path.expanduser(arg))
                for afile in files:
                    # returns a boolean telling us if it were read and either a
                    # tuple or the original filepath for reading by a source
                    result = self._read_file(afile, **kwargs)
                    data_header_pairs, filepaths = _apply_result(data_header_pairs, filepaths,
                                                                 result)

            # Already a TimeSeries
            elif isinstance(arg, GenericTimeSeries):
                already_timeseries.append(arg)

            # A URL
            elif (isinstance(arg, str) and
                  _is_url(arg)):
                url = arg
                path = download_file(url, get_and_create_download_dir())
                result = self._read_file(path, **kwargs)
                data_header_pairs, filepaths = _apply_result(data_header_pairs, filepaths, result)
            else:
                raise NoMatchError("File not found or invalid input")
            i += 1

        # TODO:
        # In the end, if there are already TimeSeries it should be put in the
        # same order as the input, currently they are not.
        return data_header_unit_tuples, data_header_pairs, already_timeseries, filepaths