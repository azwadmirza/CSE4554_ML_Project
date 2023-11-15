    def from_config(
        cls: Type,
        catalog: Optional[Dict[str, Dict[str, Any]]],
        credentials: Dict[str, Dict[str, Any]] = None,
        load_versions: Dict[str, str] = None,
        save_version: str = None,
        journal: Journal = None,
    ) -> "DataCatalog":
        """Create a ``DataCatalog`` instance from configuration. This is a
        factory method used to provide developers with a way to instantiate
        ``DataCatalog`` with configuration parsed from configuration files.

        Args:
            catalog: A dictionary whose keys are the data set names and
                the values are dictionaries with the constructor arguments
                for classes implementing ``AbstractDataSet``. The data set
                class to be loaded is specified with the key ``type`` and their
                fully qualified class name. All ``kedro.io`` data set can be
                specified by their class name only, i.e. their module name
                can be omitted.
            credentials: A dictionary containing credentials for different
                data sets. Use the ``credentials`` key in a ``AbstractDataSet``
                to refer to the appropriate credentials as shown in the example
                below.
            load_versions: A mapping between dataset names and versions
                to load. Has no effect on data sets without enabled versioning.
            save_version: Version string to be used for ``save`` operations
                by all data sets with enabled versioning. It must: a) be a
                case-insensitive string that conforms with operating system
                filename limitations, b) always return the latest version when
                sorted in lexicographical order.
            journal: Instance of Journal.

        Returns:
            An instantiated ``DataCatalog`` containing all specified
            data sets, created and ready to use.

        Raises:
            DataSetError: When the method fails to create any of the data
                sets from their config.

        Example:
        ::

            >>> config = {
            >>>     "cars": {
            >>>         "type": "CSVLocalDataSet",
            >>>         "filepath": "cars.csv",
            >>>         "save_args": {
            >>>             "index": False
            >>>         }
            >>>     },
            >>>     "boats": {
            >>>         "type": "CSVS3DataSet",
            >>>         "filepath": "boats.csv",
            >>>         "bucket_name": "mck-147789798-bucket",
            >>>         "credentials": "boats_credentials"
            >>>         "save_args": {
            >>>             "index": False
            >>>         }
            >>>     }
            >>> }
            >>>
            >>> credentials = {
            >>>     "boats_credentials": {
            >>>         "aws_access_key_id": "<your key id>",
            >>>         "aws_secret_access_key": "<your secret>"
            >>>      }
            >>> }
            >>>
            >>> catalog = DataCatalog.from_config(config, credentials)
            >>>
            >>> df = catalog.load("cars")
            >>> catalog.save("boats", df)
        """
        data_sets = {}
        catalog = copy.deepcopy(catalog) or {}
        credentials = copy.deepcopy(credentials) or {}
        run_id = journal.run_id if journal else None
        save_version = save_version or run_id or generate_timestamp()
        load_versions = copy.deepcopy(load_versions) or {}

        missing_keys = load_versions.keys() - catalog.keys()
        if missing_keys:
            warn(
                "`load_versions` keys [{}] are not found in the catalog.".format(
                    ", ".join(sorted(missing_keys))
                )
            )

        for ds_name, ds_config in catalog.items():
            ds_config = _resolve_credentials(ds_config, credentials)
            data_sets[ds_name] = AbstractDataSet.from_config(
                ds_name, ds_config, load_versions.get(ds_name), save_version
            )
        return cls(data_sets=data_sets, journal=journal)