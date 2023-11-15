def load(file):
    header = read_file_header(file)
    file = open_decompression_file(file, header.compress)

    try:
        buf = file.read()
    finally:
        if header.compress != CompressType.NONE:
            file.close()

    if header.type == SerialType.ARROW:
        return deserialize(memoryview(buf))
    else:
        return _patch_pandas_mgr(pickle.loads(buf))  # nosec