def _get_engine_from_magic_number(filename_or_obj):
    # check byte header to determine file type
    if isinstance(filename_or_obj, bytes):
        magic_number = filename_or_obj[:8]
    else:
        if filename_or_obj.tell() != 0:
            raise ValueError(
                "file-like object read/write pointer not at zero "
                "please close and reopen, or use a context "
                "manager"
            )
        magic_number = filename_or_obj.read(8)
        filename_or_obj.seek(0)

    if magic_number.startswith(b"CDF"):
        engine = "scipy"
    elif magic_number.startswith(b"\211HDF\r\n\032\n"):
        engine = "h5netcdf"
        if isinstance(filename_or_obj, bytes):
            raise ValueError(
                "can't open netCDF4/HDF5 as bytes "
                "try passing a path or file-like object"
            )
    else:
        if isinstance(filename_or_obj, bytes) and len(filename_or_obj) > 80:
            filename_or_obj = filename_or_obj[:80] + b"..."
        raise ValueError(
            "{} is not a valid netCDF file "
            "did you mean to pass a string for a path instead?".format(filename_or_obj)
        )
    return engine