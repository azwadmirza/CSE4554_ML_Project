    def _parse_args(self, *args, **kwargs):
        """
        Parses an args list for data-header pairs.  args can contain any
        mixture of the following entries:
        * tuples of data,header
        * data, header not in a tuple
        * filename, which will be read
        * directory, from which all files will be read
        * glob, from which all files will be read
        * url, which will be downloaded and read
        * lists containing any of the above.

        Example
        -------
        self._parse_args(data, header,
                         (data, header),
                         ['file1', 'file2', 'file3'],
                         'file4',
                         'directory1',
                         '*.fits')

        """

        data_header_pairs = list()
        already_maps = list()

        # Account for nested lists of items
        args = expand_list(args)

        # For each of the arguments, handle each of the cases
        i = 0
        while i < len(args):

            arg = args[i]

            # Data-header pair in a tuple
            if ((type(arg) in [tuple, list]) and
                len(arg) == 2 and
                isinstance(arg[0], np.ndarray) and
                self._validate_meta(arg[1])):

                arg[1] = OrderedDict(arg[1])
                data_header_pairs.append(arg)

            # Data-header pair not in a tuple
            elif (isinstance(arg, np.ndarray) and
                  self._validate_meta(args[i+1])):

                pair = (args[i], OrderedDict(args[i+1]))
                data_header_pairs.append(pair)
                i += 1 # an extra increment to account for the data-header pairing

            # File name
            elif (isinstance(arg,six.string_types) and
                  os.path.isfile(os.path.expanduser(arg))):
                path = os.path.expanduser(arg)
                pairs = self._read_file(path, **kwargs)
                data_header_pairs += pairs

            # Directory
            elif (isinstance(arg,six.string_types) and
                  os.path.isdir(os.path.expanduser(arg))):
                path = os.path.expanduser(arg)
                files = [os.path.join(path, elem) for elem in os.listdir(path)]
                for afile in files:
                    data_header_pairs += self._read_file(afile, **kwargs)

            # Glob
            elif (isinstance(arg,six.string_types) and '*' in arg):
                files = glob.glob( os.path.expanduser(arg) )
                for afile in files:
                    data_header_pairs += self._read_file(afile, **kwargs)

            # Already a Map
            elif isinstance(arg, GenericMap):
                already_maps.append(arg)

            # A URL
            elif (isinstance(arg,six.string_types) and
                  _is_url(arg)):
                default_dir = sunpy.config.get("downloads", "download_dir")
                url = arg
                path = download_file(url, default_dir)
                pairs = self._read_file(path, **kwargs)
                data_header_pairs += pairs

            # A database Entry
            elif isinstance(arg, DatabaseEntry):
                data_header_pairs += self._read_file(arg.path, **kwargs)

            else:
                raise ValueError("File not found or invalid input")

            i += 1
        #TODO:
        # In the end, if there are already maps it should be put in the same
        # order as the input, currently they are not.
        return data_header_pairs, already_maps