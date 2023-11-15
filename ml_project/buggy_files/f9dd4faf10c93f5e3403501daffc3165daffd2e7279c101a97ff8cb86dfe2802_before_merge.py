def read_sigmf(
    data_file, meta_file=None, buffer=None, num_samples=None, offset=0
):
    """
    Read and unpack binary file, with SigMF spec, to GPU memory.

    Parameters
    ----------
    data_file : str
        File contain sigmf data.
    meta_file : str, optional
        File contain sigmf meta.
    buffer : ndarray, optional
        Pinned memory buffer to use when copying data from GPU.
    num_samples : int, optional
        Number of samples to be loaded to GPU. If set to 0,
        read in all samples.
    offset : int, optional
        May be specified as a non-negative integer offset.
        It is the number of samples before loading 'num_samples'.
        'offset' must be a multiple of ALLOCATIONGRANULARITY which
        is equal to PAGESIZE on Unix systems.

    Returns
    -------
    out : ndarray
        An 1-dimensional array containing unpacked binary data.

    """

    if meta_file is None:
        meta_ext = ".sigmf-meta"

        split_string = data_file.split(".")
        meta_file = split_string[0] + meta_ext

    with open(meta_file, "r") as f:
        header = json.loads(f.read())

    dataset_type = _extract_values(header, "core:datatype")

    data_type = dataset_type[0].split("_")

    if len(data_type) == 1:
        endianness = "N"
    elif len(data_type) == 2:
        if data_type[1] == "le":
            endianness = "L"
        elif data_type[1] == "be":
            endianness = "B"
        else:
            raise NotImplementedError
    else:
        raise NotImplementedError

    # Complex
    if data_type[0][0] == "c":
        if data_type[0][1:] == "f64":
            data_type = cp.complex128
        elif data_type[0][1:] == "f32":
            data_type = cp.complex64
        elif data_type[0][1:] == "i32":
            data_type = cp.int32
        elif data_type[0][1:] == "u32":
            data_type = cp.uint32
        elif data_type[0][1:] == "i16":
            data_type = cp.int16
        elif data_type[0][1:] == "u16":
            data_type = cp.uint16
        elif data_type[0][1:] == "i8":
            data_type = cp.int8
        elif data_type[0][1:] == "u8":
            data_type = cp.uint8
        else:
            raise NotImplementedError
    # Real
    elif data_type[0][0] == "r":
        if data_type[0][1:] == "f64":
            data_type = cp.float64
        elif data_type[0][1:] == "f32":
            data_type = cp.float32
        elif data_type[0][1:] == "i32":
            data_type = cp.int32
        elif data_type[0][1:] == "u32":
            data_type = cp.uint32
        elif data_type[0][1:] == "i16":
            data_type = cp.int16
        elif data_type[0][1:] == "u16":
            data_type = cp.uint16
        elif data_type[0][1:] == "i8":
            data_type = cp.int8
        elif data_type[0][1:] == "u8":
            data_type = cp.uint8
        else:
            raise NotImplementedError

    else:
        raise NotImplementedError

    binary = read_bin(data_file, buffer, data_type, num_samples, offset)

    out = unpack_bin(binary, data_type, endianness)

    return out