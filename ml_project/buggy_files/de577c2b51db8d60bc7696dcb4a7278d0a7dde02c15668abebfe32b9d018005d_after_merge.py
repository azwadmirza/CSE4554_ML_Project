    def open(
        cls,
        filename,
        mode="r",
        format="NETCDF4",
        group=None,
        clobber=True,
        diskless=False,
        persist=False,
        lock=None,
        lock_maker=None,
        autoclose=False,
    ):
        import netCDF4

        if not isinstance(filename, str):
            raise ValueError(
                "can only read bytes or file-like objects "
                "with engine='scipy' or 'h5netcdf'"
            )

        if format is None:
            format = "NETCDF4"

        if lock is None:
            if mode == "r":
                if is_remote_uri(filename):
                    lock = NETCDFC_LOCK
                else:
                    lock = NETCDF4_PYTHON_LOCK
            else:
                if format is None or format.startswith("NETCDF4"):
                    base_lock = NETCDF4_PYTHON_LOCK
                else:
                    base_lock = NETCDFC_LOCK
                lock = combine_locks([base_lock, get_write_lock(filename)])

        kwargs = dict(
            clobber=clobber, diskless=diskless, persist=persist, format=format
        )
        manager = CachingFileManager(
            netCDF4.Dataset, filename, mode=mode, kwargs=kwargs
        )
        return cls(manager, group=group, mode=mode, lock=lock, autoclose=autoclose)