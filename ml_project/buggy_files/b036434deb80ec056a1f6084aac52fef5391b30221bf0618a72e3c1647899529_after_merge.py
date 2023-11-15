    def __init__(  # pylint: disable=too-many-arguments
        self,
        path: str,
        dataset: Union[str, Type[AbstractDataSet], Dict[str, Any]],
        filepath_arg: str = "filepath",
        filename_suffix: str = "",
        credentials: Dict[str, Any] = None,
        load_args: Dict[str, Any] = None,
    ):
        """Creates a new instance of ``PartitionedDataSet``.

        Args:
            path: Path to the folder containing partitioned data.
                If path starts with the protocol (e.g., ``s3://``) then the
                corresponding ``fsspec`` concrete filesystem implementation will
                be used. If protocol is not specified,
                ``fsspec.implementations.local.LocalFileSystem`` will be used.
                **Note:** Some concrete implementations are bundled with ``fsspec``,
                while others (like ``s3`` or ``gcs``) must be installed separately
                prior to usage of the ``PartitionedDataSet``.
            dataset: Underlying dataset definition. This is used to instantiate
                the dataset for each file located inside the ``path``.
                Accepted formats are:
                a) object of a class that inherits from ``AbstractDataSet``
                b) a string representing a fully qualified class name to such class
                c) a dictionary with ``type`` key pointing to a string from b),
                other keys are passed to the Dataset initializer.
                Credentials for the dataset can be explicitly specified in
                this configuration.
            filepath_arg: Underlying dataset initializer argument that will
                contain a path to each corresponding partition file.
                If unspecified, defaults to "filepath".
            filename_suffix: If specified, only partitions that end with this
                string will be processed.
            credentials: Protocol-specific options that will be passed to
                ``fsspec.filesystem``
                https://filesystem-spec.readthedocs.io/en/latest/api.html#fsspec.filesystem
                and the dataset initializer. If the dataset config contains
                explicit credentials spec, then such spec will take precedence.
                **Note:** ``dataset_credentials`` key has now been deprecated
                and should not be specified.
                All possible credentials management scenarios are documented here:
                https://kedro.readthedocs.io/en/latest/04_user_guide/08_advanced_io.html#partitioned-dataset-credentials
            load_args: Keyword arguments to be passed into ``find()`` method of
                the filesystem implementation.

        Raises:
            DataSetError: If versioning is enabled for the underlying dataset.
        """
        super().__init__()

        self._path = path
        self._filename_suffix = filename_suffix
        self._protocol = infer_storage_options(self._path)["protocol"]

        dataset = dataset if isinstance(dataset, dict) else {"type": dataset}
        self._dataset_type, self._dataset_config = parse_dataset_definition(dataset)
        if VERSION_KEY in self._dataset_config:
            raise DataSetError(
                "`{}` does not support versioning of the underlying dataset. "
                "Please remove `{}` flag from the dataset definition.".format(
                    self.__class__.__name__, VERSIONED_FLAG_KEY
                )
            )

        self._credentials, dataset_credentials = _split_credentials(credentials)
        if dataset_credentials:
            if CREDENTIALS_KEY in self._dataset_config:
                self._logger.warning(
                    "Top-level credentials will not propagate into the "
                    "underlying dataset since credentials were explicitly "
                    "defined in the dataset config."
                )
            else:
                self._dataset_config[CREDENTIALS_KEY] = dataset_credentials

        self._filepath_arg = filepath_arg
        if self._filepath_arg in self._dataset_config:
            warn(
                "`{}` key must not be specified in the dataset definition as it "
                "will be overwritten by partition path".format(self._filepath_arg)
            )

        self._load_args = deepcopy(load_args) or {}
        self._sep = self._filesystem.sep
        # since some filesystem implementations may implement a global cache
        self.invalidate_cache()