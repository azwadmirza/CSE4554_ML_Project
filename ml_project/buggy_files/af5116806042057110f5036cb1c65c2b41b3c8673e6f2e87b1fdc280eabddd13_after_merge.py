    def __init__(self, meta: dict, daskarray, delayed_objs: tuple = None):
        if "dask" not in sys.modules:
            raise ModuleNotInstalledException("dask")
        else:
            import dask
            import dask.array

            global dask

        if not meta.get("preprocessed"):
            meta = Tensor._preprocess_meta(meta, daskarray)
        self._meta = meta
        self._array = daskarray
        self._delayed_objs = delayed_objs
        self._shape = _dask_shape_backward(daskarray.shape)
        self._dtype = meta["dtype"]
        self._dtag = meta.get("dtag")
        self._dcompress = meta.get("dcompress")
        self._dcompress_algo = meta.get("dcompress_algo")
        self._dcompress_lvl = meta.get("dcompress_lvl")
        self._chunksize = meta.get("chunksize")