def get_handle(
    path_or_buf,
    mode: str,
    encoding=None,
    compression: Optional[Union[str, Mapping[str, Any]]] = None,
    memory_map: bool = False,
    is_text: bool = True,
):
    """
    Get file handle for given path/buffer and mode.

    Parameters
    ----------
    path_or_buf : str or file handle
        File path or object.
    mode : str
        Mode to open path_or_buf with.
    encoding : str or None
        Encoding to use.
    compression : str or dict, default None
        If string, specifies compression mode. If dict, value at key 'method'
        specifies compression mode. Compression mode must be one of {'infer',
        'gzip', 'bz2', 'zip', 'xz', None}. If compression mode is 'infer'
        and `filepath_or_buffer` is path-like, then detect compression from
        the following extensions: '.gz', '.bz2', '.zip', or '.xz' (otherwise
        no compression). If dict and compression mode is one of
        {'zip', 'gzip', 'bz2'}, or inferred as one of the above,
        other entries passed as additional compression options.

        .. versionchanged:: 1.0.0

           May now be a dict with key 'method' as compression mode
           and other keys as compression options if compression
           mode is 'zip'.

        .. versionchanged:: 1.1.0

           Passing compression options as keys in dict is now
           supported for compression modes 'gzip' and 'bz2' as well as 'zip'.

    memory_map : boolean, default False
        See parsers._parser_params for more information.
    is_text : boolean, default True
        whether file/buffer is in text format (csv, json, etc.), or in binary
        mode (pickle, etc.).

    Returns
    -------
    f : file-like
        A file-like object.
    handles : list of file-like objects
        A list of file-like object that were opened in this function.
    """
    need_text_wrapping: Tuple[Type["IOBase"], ...]
    try:
        from s3fs import S3File

        need_text_wrapping = (BufferedIOBase, RawIOBase, S3File)
    except ImportError:
        need_text_wrapping = (BufferedIOBase, RawIOBase)

    handles: List[IO] = list()
    f = path_or_buf

    # Convert pathlib.Path/py.path.local or string
    path_or_buf = stringify_path(path_or_buf)
    is_path = isinstance(path_or_buf, str)

    compression, compression_args = get_compression_method(compression)
    if is_path:
        compression = infer_compression(path_or_buf, compression)

    if compression:

        # GH33398 the type ignores here seem related to mypy issue #5382;
        # it may be possible to remove them once that is resolved.

        # GZ Compression
        if compression == "gzip":
            if is_path:
                f = gzip.open(
                    path_or_buf, mode, **compression_args  # type: ignore
                )
            else:
                f = gzip.GzipFile(
                    fileobj=path_or_buf, **compression_args  # type: ignore
                )

        # BZ Compression
        elif compression == "bz2":
            if is_path:
                f = bz2.BZ2File(
                    path_or_buf, mode, **compression_args  # type: ignore
                )
            else:
                f = bz2.BZ2File(path_or_buf, **compression_args)  # type: ignore

        # ZIP Compression
        elif compression == "zip":
            zf = _BytesZipFile(path_or_buf, mode, **compression_args)
            # Ensure the container is closed as well.
            handles.append(zf)
            if zf.mode == "w":
                f = zf
            elif zf.mode == "r":
                zip_names = zf.namelist()
                if len(zip_names) == 1:
                    f = zf.open(zip_names.pop())
                elif len(zip_names) == 0:
                    raise ValueError(f"Zero files found in ZIP file {path_or_buf}")
                else:
                    raise ValueError(
                        "Multiple files found in ZIP file. "
                        f"Only one file per ZIP: {zip_names}"
                    )

        # XZ Compression
        elif compression == "xz":
            f = _get_lzma_file(lzma)(path_or_buf, mode)

        # Unrecognized Compression
        else:
            msg = f"Unrecognized compression type: {compression}"
            raise ValueError(msg)

        handles.append(f)

    elif is_path:
        if encoding:
            # Encoding
            f = open(path_or_buf, mode, encoding=encoding, newline="")
        elif is_text:
            # No explicit encoding
            f = open(path_or_buf, mode, errors="replace", newline="")
        else:
            # Binary mode
            f = open(path_or_buf, mode)
        handles.append(f)

    # Convert BytesIO or file objects passed with an encoding
    if is_text and (compression or isinstance(f, need_text_wrapping)):
        from io import TextIOWrapper

        g = TextIOWrapper(f, encoding=encoding, newline="")
        if not isinstance(f, (BufferedIOBase, RawIOBase)):
            handles.append(g)
        f = g

    if memory_map and hasattr(f, "fileno"):
        try:
            wrapped = _MMapWrapper(f)
            f.close()
            f = wrapped
        except Exception:
            # we catch any errors that may have occurred
            # because that is consistent with the lower-level
            # functionality of the C engine (pd.read_csv), so
            # leave the file handler as is then
            pass

    return f, handles