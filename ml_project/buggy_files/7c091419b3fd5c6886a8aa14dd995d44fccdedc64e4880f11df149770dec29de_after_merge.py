def loads(buf):
    mv = memoryview(buf)
    header = read_file_header(mv)
    compress = header.compress

    if compress == CompressType.NONE:
        data = buf[HEADER_LENGTH:]
    else:
        data = decompressors[compress](mv[HEADER_LENGTH:])

    if header.type == SerialType.ARROW:
        try:
            return deserialize(memoryview(data))
        except pyarrow.lib.ArrowInvalid:  # pragma: no cover
            # reconstruct value from buffers of arrow components
            data_view = memoryview(data)
            meta_block_size = np.frombuffer(data_view[0:4], dtype='int32').item()
            meta = pickle.loads(data_view[4:4 + meta_block_size])  # nosec
            buffer_sizes = meta.pop('buffer_sizes')
            bounds = np.cumsum([4 + meta_block_size] + buffer_sizes)
            meta['data'] = [pyarrow.py_buffer(data_view[bounds[idx]:bounds[idx + 1]])
                            for idx in range(len(buffer_sizes))]
            return _patch_pandas_mgr(pyarrow.deserialize_components(meta, mars_serialize_context()))
    else:
        return _patch_pandas_mgr(pickle.loads(data))  # nosec