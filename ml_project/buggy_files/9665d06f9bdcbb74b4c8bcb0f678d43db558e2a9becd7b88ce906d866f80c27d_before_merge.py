    def __dask_scheduler__(self):
        return self._to_temp_dataset().__dask_optimize__