    def __init__(self, filenames=None, reader=None, filter_parameters=None, reader_kwargs=None,
                 ppp_config_dir=get_environ_config_dir(),
                 base_dir=None,
                 sensor=None,
                 start_time=None,
                 end_time=None,
                 area=None):
        """Initialize Scene with Reader and Compositor objects.

        To load data `filenames` and preferably `reader` must be specified. If `filenames` is provided without `reader`
        then the available readers will be searched for a Reader that can support the provided files. This can take
        a considerable amount of time so it is recommended that `reader` always be provided. Note without `filenames`
        the Scene is created with no Readers available requiring Datasets to be added manually::

            scn = Scene()
            scn['my_dataset'] = Dataset(my_data_array, **my_info)

        Args:
            filenames (iterable or dict): A sequence of files that will be used to load data from. A ``dict`` object
                                          should map reader names to a list of filenames for that reader.
            reader (str or list): The name of the reader to use for loading the data or a list of names.
            filter_parameters (dict): Specify loaded file filtering parameters.
                                      Shortcut for `reader_kwargs['filter_parameters']`.
            reader_kwargs (dict): Keyword arguments to pass to specific reader instances.
            ppp_config_dir (str): The directory containing the configuration files for satpy.
            base_dir (str): (DEPRECATED) The directory to search for files containing the
                            data to load. If *filenames* is also provided,
                            this is ignored.
            sensor (list or str): (DEPRECATED: Use `find_files_and_readers` function) Limit used files by provided
                                  sensors.
            area (AreaDefinition): (DEPRECATED: Use `filter_parameters`) Limit used files by geographic area.
            start_time (datetime): (DEPRECATED: Use `filter_parameters`) Limit used files by starting time.
            end_time (datetime): (DEPRECATED: Use `filter_parameters`) Limit used files by ending time.

        """
        super(Scene, self).__init__()
        # Set the PPP_CONFIG_DIR in the environment in case it's used elsewhere in pytroll
        LOG.debug("Setting 'PPP_CONFIG_DIR' to '%s'", ppp_config_dir)
        os.environ["PPP_CONFIG_DIR"] = self.ppp_config_dir = ppp_config_dir

        if not filenames and (start_time or end_time or base_dir):
            import warnings
            warnings.warn(
                "Deprecated: Use " + \
                "'from satpy import find_files_and_readers' to find files")
            from satpy import find_files_and_readers
            filenames = find_files_and_readers(
                start_time=start_time,
                end_time=end_time,
                base_dir=base_dir,
                reader=reader,
                sensor=sensor,
                ppp_config_dir=self.ppp_config_dir,
                reader_kwargs=reader_kwargs,
            )
        elif start_time or end_time or area:
            import warnings
            warnings.warn(
                "Deprecated: Use " + \
                "'filter_parameters' to filter loaded files by 'start_time', " + \
                "'end_time', or 'area'.")
            fp = filter_parameters if filter_parameters else {}
            fp.update({
                'start_time': start_time,
                'end_time': end_time,
                'area': area,
            })
            filter_parameters = fp
        if filter_parameters:
            if reader_kwargs is None:
                reader_kwargs = {}
            reader_kwargs.setdefault('filter_parameters', {}).update(filter_parameters)

        self.readers = self.create_reader_instances(filenames=filenames,
                                                    reader=reader,
                                                    reader_kwargs=reader_kwargs)
        self.info.update(self._compute_metadata_from_readers())
        self.datasets = DatasetDict()
        self.cpl = CompositorLoader(self.ppp_config_dir)
        comps, mods = self.cpl.load_compositors(self.info['sensor'])
        self.wishlist = set()
        self.dep_tree = DependencyTree(self.readers, comps, mods)