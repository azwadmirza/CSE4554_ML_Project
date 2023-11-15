    def __init__(self, values, dtype: ArrowDtype = None, copy=False):
        pandas_only = self._pandas_only()

        if pa is not None and not pandas_only:
            self._init_by_arrow(values, dtype=dtype, copy=copy)
        elif not is_kernel_mode():
            # not in kernel mode, allow to use numpy handle data
            # just for infer dtypes purpose
            self._init_by_numpy(values, dtype=dtype, copy=copy)
        else:
            raise ImportError('Cannot create ArrowArray '
                              'when `pyarrow` not installed')

        # for test purpose
        self._force_use_pandas = pandas_only