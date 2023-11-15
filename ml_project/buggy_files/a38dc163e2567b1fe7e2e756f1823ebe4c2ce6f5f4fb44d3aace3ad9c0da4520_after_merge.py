def _get_engine_from_magic_number(filename_or_obj):
    # check byte header to determine file type
    if isinstance(filename_or_obj, bytes):
        magic_number = filename_or_obj[:8]
    else:
        if filename_or_obj.tell() != 0:
            raise ValueError(
                "file-like object read/write pointer not at zero "
                "please close and reopen, or use a context manager"
            )
        magic_number = filename_or_obj.read(8)
        filename_or_obj.seek(0)

    if magic_number.startswith(b"CDF"):
        engine = "scipy"
    elif magic_number.startswith(b"\211HDF\r\n\032\n"):
        engine = "h5netcdf"
    else:
        raise ValueError(
            f"{magic_number} is not the signature of any supported file format "
            "did you mean to pass a string for a path instead?"
        )
    return engine