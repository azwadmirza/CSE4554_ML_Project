def load(file):
    header = read_file_header(file)
    file = open_decompression_file(file, header.compress)

    try:
        buf = file.read()
    finally:
        if header.compress != CompressType.NONE:
            file.close()

    if header.type == SerialType.ARROW:
        return pyarrow.deserialize(memoryview(buf), mars_serialize_context())
    else:
        return pickle.loads(buf)