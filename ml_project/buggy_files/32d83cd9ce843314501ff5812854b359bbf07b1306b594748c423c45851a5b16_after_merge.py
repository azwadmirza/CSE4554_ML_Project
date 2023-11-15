    def __init__(
        self,
        url: str,
        mode: str = "a",
        shape=None,
        schema=None,
        token=None,
        fs=None,
        fs_map=None,
        cache: int = defaults.DEFAULT_MEMORY_CACHE_SIZE,
        storage_cache: int = defaults.DEFAULT_STORAGE_CACHE_SIZE,
        lock_cache=True,
        tokenizer=None,
    ):
        """| Open a new or existing dataset for read/write

        Parameters
        ----------
        url: str
            The url where dataset is located/should be created
        mode: str, optional (default to "a")
            Python way to tell whether dataset is for read or write (ex. "r", "w", "a")
        shape: tuple, optional
            Tuple with (num_samples,) format, where num_samples is number of samples
        schema: optional
            Describes the data of a single sample. Hub schemas are used for that
            Required for 'a' and 'w' modes
        token: str or dict, optional
            If url is refering to a place where authorization is required,
            token is the parameter to pass the credentials, it can be filepath or dict
        fs: optional
        fs_map: optional
        cache: int, optional
            Size of the memory cache. Default is 64MB (2**26)
            if 0, False or None, then cache is not used
        storage_cache: int, optional
            Size of the storage cache. Default is 256MB (2**28)
            if 0, False or None, then storage cache is not used
        lock_cache: bool, optional
            Lock the cache for avoiding multiprocessing errors
        """

        shape = norm_shape(shape)
        if len(shape) != 1:
            raise ShapeLengthException()
        mode = mode or "a"
        storage_cache = norm_cache(storage_cache) if cache else 0
        cache = norm_cache(cache)
        schema: SchemaDict = featurify(schema) if schema else None

        self._url = url
        self._token = token
        self._mode = mode
        self.tokenizer = tokenizer

        self._fs, self._path = (
            (fs, url) if fs else get_fs_and_path(self._url, token=token)
        )
        self._cache = cache
        self._storage_cache = storage_cache
        self.lock_cache = lock_cache
        self.verison = "1.x"

        needcreate = self._check_and_prepare_dir()
        fs_map = fs_map or get_storage_map(
            self._fs, self._path, cache, lock=lock_cache, storage_cache=storage_cache
        )
        self._fs_map = fs_map
        self.username = None
        self.dataset_name = None
        if not needcreate:
            self.meta = json.loads(fs_map["meta.json"].decode("utf-8"))
            self._shape = tuple(self.meta["shape"])
            self._schema = hub.schema.deserialize.deserialize(self.meta["schema"])
            self._flat_tensors = tuple(flatten(self.schema))
            self._tensors = dict(self._open_storage_tensors())
            if shape != (None,) and shape != self._shape:
                raise TypeError(
                    f"Shape in metafile [{self._shape}]  and shape in arguments [{shape}] are !=, use mode='w' to overwrite dataset"
                )
            if schema is not None and sorted(schema.dict_.keys()) != sorted(
                self._schema.dict_.keys()
            ):
                raise TypeError(
                    "Schema in metafile and schema in arguments do not match, use mode='w' to overwrite dataset"
                )

        else:
            if shape[0] is None:
                raise ShapeArgumentNotFoundException()
            if schema is None:
                raise SchemaArgumentNotFoundException()
            try:
                if shape is None:
                    raise ShapeArgumentNotFoundException()
                if schema is None:
                    raise SchemaArgumentNotFoundException()
                self._schema = schema
                self._shape = tuple(shape)
                self.meta = self._store_meta()
                self._flat_tensors = tuple(flatten(self.schema))
                self._tensors = dict(self._generate_storage_tensors())
                self.flush()
            except Exception as e:
                try:
                    self.close()
                except Exception:
                    pass
                self._fs.rm(self._path, recursive=True)
                logger.error("Deleting the dataset " + traceback.format_exc() + str(e))
                raise

        if needcreate and (
            self._path.startswith("s3://snark-hub-dev/")
            or self._path.startswith("s3://snark-hub/")
        ):
            subpath = self._path[5:]
            spl = subpath.split("/")
            if len(spl) < 4:
                raise ValueError("Invalid Path for dataset")
            self.username = spl[-2]
            self.dataset_name = spl[-1]
            HubControlClient().create_dataset_entry(
                self.username, self.dataset_name, self.meta
            )